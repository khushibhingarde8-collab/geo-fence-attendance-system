from flask import Blueprint, jsonify, request, send_file
from config import mysql
from MySQLdb.cursors import DictCursor
from datetime import datetime, date, timedelta
import calendar
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import landscape, A4

import io


monthly_report_bp = Blueprint(
    "monthly_report",
    __name__
)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def is_weekly_off(dt):
    """
    Weekly Off:
    Sunday
    +
    2nd & 4th Saturday
    """

    # Sunday
    if dt.weekday() == 6:
        return True

    # Saturday
    if dt.weekday() == 5:

        saturday_no = ((dt.day - 1) // 7) + 1

        if saturday_no in [2, 4]:
            return True

    return False


def is_holiday(cur, dt):

    cur.execute("""

        SELECT holiday_name

        FROM holiday_master

        WHERE holiday_date=%s

    """, (dt,))

    return cur.fetchone()


def is_leave(cur, employee_id, dt):

    cur.execute("""

        SELECT leave_type

        FROM tbl_leaves

        WHERE employee_id=%s

        AND status='Approved'

        AND %s BETWEEN start_date AND end_date

    """, (employee_id, dt))

    return cur.fetchone()


def get_attendance(cur, employee_id, dt):

    cur.execute("""

        SELECT *

        FROM attendance_master

        WHERE employee_id=%s

        AND attendance_date=%s

    """, (employee_id, dt))

    return cur.fetchone()


# ==========================================================
# GET DEPARTMENTS
# ==========================================================

@monthly_report_bp.route(
    "/api/get_departments",
    methods=["GET"]
)
def get_departments():

    try:

        cur = mysql.connection.cursor(DictCursor)

        cur.execute("""

            SELECT

            department_id,
            department_name

            FROM tbl_department

            WHERE is_active=TRUE

            ORDER BY department_name

        """)

        data = cur.fetchall()

        cur.close()

        return jsonify(data)

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# ==========================================================
# MONTHLY MATRIX REPORT
# ==========================================================

@monthly_report_bp.route(
    "/api/monthly_matrix_report",
    methods=["GET"]
)
def monthly_matrix_report():

    try:

        month = int(request.args.get("month"))
        year = int(request.args.get("year"))

        department = request.args.get("department")
        employee_id = request.args.get("employee_id")

        cur = mysql.connection.cursor(DictCursor)

        query = """

        SELECT

            e.employee_id,

            e.employee_code,

            CONCAT(
                e.first_name,
                ' ',
                e.last_name
            ) AS employee_name,

            d.department_name

        FROM employees e

        LEFT JOIN tbl_department d

        ON e.department_id=d.department_id

        WHERE e.is_active=TRUE

        """

        params = []

        if department and department != "All":

            query += """

            AND d.department_name=%s

            """

            params.append(department)

        if employee_id:

            query += """

            AND e.employee_id=%s

            """

            params.append(employee_id)

        query += """

        ORDER BY employee_name

        """

        cur.execute(query, params)

        employees = cur.fetchall()

        report = []

        days = calendar.monthrange(year, month)[1]

        for emp in employees:

            present = 0
            half_day = 0
            absent = 0
            leave = 0
            holiday = 0
            weekly_off = 0

            attendance = {}

            for d in range(1, days + 1):

                current = date(year, month, d)

                status = "-"

                # 1. Holiday
                holiday_row = is_holiday(cur, current)

                if holiday_row:

                    status = "H"
                    holiday += 1

                # 2. Approved Leave
                elif is_leave(cur, emp["employee_id"], current):

                    status = "L"
                    leave += 1

                # 3. Weekly Off
                elif is_weekly_off(current):

                    status = "WO"
                    weekly_off += 1

                # 4. Attendance
                else:

                    att = get_attendance(
                        cur,
                        emp["employee_id"],
                        current
                    )

                    if att:

                        db_status = (att["status"] or "").strip()

                        if db_status in ["Present", "Full Day"]:

                            status = "P"
                            present += 1

                        elif db_status == "Half Day":

                            status = "HD"
                            half_day += 1

                        elif db_status == "Absent":

                            status = "A"
                            absent += 1

                        else:

                            status = "-"

                    else:

                        status = "A"
                        absent += 1

                attendance[f"{d:02d}"] = status

            report.append({

                "employee_id": emp["employee_id"],

                "employee_code": emp["employee_code"],

                "employee_name": emp["employee_name"],

                "department": emp["department_name"],

                "attendance": attendance,

                "summary": {

                    "present": present,

                    "half_day": half_day,

                    "absent": absent,

                    "leave": leave,

                    "holiday": holiday,

                    "weekly_off": weekly_off

                }

            })

        cur.close()

        return jsonify({

            "status": "success",

            "data": report,

            "employees": report

        })

    except Exception as e:

        print("MONTHLY MATRIX ERROR :", e)

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

# ==========================================================
# EMPLOYEE MONTHLY DETAIL REPORT
# ==========================================================

@monthly_report_bp.route(
    "/api/monthly_detailed_report",
    methods=["GET"]
)
def monthly_detailed_report():

    try:

        employee_id = int(request.args.get("employee_id"))
        month = int(request.args.get("month"))
        year = int(request.args.get("year"))

        cur = mysql.connection.cursor(DictCursor)

        # --------------------------------------------------
        # Employee Details
        # --------------------------------------------------

        cur.execute("""

            SELECT

                e.employee_code,

                CONCAT(
                    e.first_name,
                    ' ',
                    e.last_name
                ) AS employee_name,

                COALESCE(
                    d.department_name,
                    'Not Assigned'
                ) AS department_name

            FROM employees e

            LEFT JOIN tbl_department d

            ON e.department_id=d.department_id

            WHERE e.employee_id=%s

        """,(employee_id,))

        emp = cur.fetchone()

        if not emp:

            cur.close()

            return jsonify({

                "status":"error",

                "message":"Employee not found"

            }),404


        present = 0
        half_day = 0
        absent = 0
        leave = 0
        holiday = 0
        weekly_off = 0
        total_hours = 0

        attendance = []

        days = calendar.monthrange(year, month)[1]

        for d in range(1, days + 1):

            current = date(year, month, d)

            status = ""

            check_in = ""
            check_out = ""
            work_hours = 0
            overtime = 0
            arrival_status = ""
            checkout_type = ""

            # -----------------------------
            # Holiday
            # -----------------------------

            holiday_row = is_holiday(cur, current)

            if holiday_row:

                status = "Holiday"
                holiday += 1

            # -----------------------------
            # Leave
            # -----------------------------

            elif is_leave(cur, employee_id, current):

                status = "Leave"
                leave += 1

            # -----------------------------
            # Weekly Off
            # -----------------------------

            elif is_weekly_off(current):

                status = "Weekly Off"
                weekly_off += 1

            # -----------------------------
            # Attendance
            # -----------------------------

            else:

                att = get_attendance(
                    cur,
                    employee_id,
                    current
                )

                if att:

                    status = att["status"] or "Absent"

                    check_in = str(att["check_in"] or "")

                    check_out = str(att["check_out"] or "")

                    work_hours = att["work_hours"] or 0

                    overtime = att["overtime_minutes"] or 0

                    arrival_status = att["arrival_status"] or ""

                    checkout_type = att["checkout_type"] or ""

                    if status in ["Present", "Full Day"]:

                        present += 1

                    elif status == "Half Day":

                        half_day += 1

                    elif status == "Absent":

                        absent += 1

                    if work_hours:

                        total_hours += float(work_hours)

                else:

                    status = "Absent"
                    absent += 1

            attendance.append({

                "date": current.strftime("%d %b %a"),

                "status": status,

                "check_in": check_in,

                "check_out": check_out,

                "work_hours": work_hours,

                "overtime_minutes": overtime,

                "arrival_status": arrival_status,

                "checkout_type": checkout_type

            })

        cur.close()

        return jsonify({

            "status": "success",

            "employee_id": employee_id,

            "employee_code": emp["employee_code"],

            "employee_name": emp["employee_name"],

            "department": emp["department_name"],

            "month": month,

            "year": year,

            "summary": {

                "present": present,

                "half_day": half_day,

                "absent": absent,

                "leave": leave,

                "holiday": holiday,

                "weekly_off": weekly_off,

                "total_hours": round(total_hours, 2)

            },

            "attendance": attendance

        })

    except Exception as e:

        print("DETAIL REPORT ERROR :", e)

        return jsonify({

            "status":"error",

            "message":str(e)

        }),500

# ==========================================================
# DOWNLOAD MONTHLY REPORT PDF
# ==========================================================

@monthly_report_bp.route(
    "/api/download_monthly_report_pdf",
    methods=["GET"]
)
def download_monthly_report_pdf():

    try:

        month = int(request.args.get("month"))
        year = int(request.args.get("year"))


        cur = mysql.connection.cursor(
            DictCursor
        )


        cur.execute("""

        SELECT

        e.employee_id,

        CONCAT(
        e.first_name,
        ' ',
        e.last_name
        ) AS employee_name,


        COALESCE(
        d.department_name,
        'Not Assigned'
        ) AS department_name,


        SUM(
        CASE
        WHEN am.status IN
        ('Present','Full Day')
        THEN 1 ELSE 0
        END
        ) AS present,


        SUM(
        CASE
        WHEN am.status='Half Day'
        THEN 1 ELSE 0
        END
        ) AS half_day,


        SUM(
        CASE
        WHEN am.status='Absent'
        THEN 1 ELSE 0
        END
        ) AS absent



        FROM employees e


        LEFT JOIN tbl_department d

        ON e.department_id=d.department_id


        LEFT JOIN attendance_master am

        ON e.employee_id=am.employee_id


        AND MONTH(am.attendance_date)=%s

        AND YEAR(am.attendance_date)=%s


        WHERE e.is_active=TRUE


        GROUP BY

        e.employee_id,
        employee_name,
        department_name


        ORDER BY employee_name


        """,
        (
            month,
            year
        ))


        rows = cur.fetchall()


        cur.close()



        buffer = io.BytesIO()


        doc = SimpleDocTemplate(

            buffer,

            pagesize=landscape(A4)

        )


        styles = getSampleStyleSheet()


        content=[]



        content.append(

            Paragraph(

                "MONTHLY ATTENDANCE REPORT",

                styles["Title"]

            )

        )


        content.append(
            Spacer(1,20)
        )


        content.append(

            Paragraph(

                f"Month : {month}<br/>Year : {year}",

                styles["Normal"]

            )

        )


        content.append(
            Spacer(1,20)
        )



        data=[

            [
                "ID",
                "Employee Name",
                "Department",
                "P",
                "HD",
                "A",
                "L",
                "H",
                "WO"
            ]

        ]



        for r in rows:


            data.append([

                r["employee_id"],

                r["employee_name"],

                r["department_name"],

                r["present"] or 0,

                r["half_day"] or 0,

                r["absent"] or 0,

                "-",

                "-",

                "-"

            ])




        table = Table(
            data
        )


        table.setStyle(

            TableStyle([


                (
                'GRID',
                (0,0),
                (-1,-1),
                1,
                None
                ),


                (
                'ALIGN',
                (0,0),
                (-1,-1),
                'CENTER'
                )

            ])

        )


        content.append(table)


        content.append(
            Spacer(1,20)
        )


        content.append(

            Paragraph(

            """
            Legend:
            P = Present |
            HD = Half Day |
            A = Absent |
            L = Leave |
            H = Holiday |
            WO = Weekly Off

            """,

            styles["Normal"]

            )

        )


        doc.build(content)


        buffer.seek(0)


        return send_file(

            buffer,

            as_attachment=True,

            download_name=
            "Monthly_Attendance_Report.pdf",

            mimetype=
            "application/pdf"

        )


    except Exception as e:


        print(
            "PDF ERROR:",
            e
        )


        return jsonify({

            "status":"error",

            "message":str(e)

        }),500        