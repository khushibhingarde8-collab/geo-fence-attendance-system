from flask import Blueprint, request, jsonify, render_template, session
from config import mysql
from database import (
    get_employee_location,
    get_deputed_location,
    mark_attendance
)
from utils import calculate_distance
import calendar

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import io

from datetime import datetime, timedelta
import pdfkit
from flask import make_response
from MySQLdb.cursors import DictCursor
import os

path_wkhtmltopdf = os.getenv("WKHTMLTOPDF_PATH")

attendance_bp = Blueprint("attendance", __name__)


# =========================================================
# GET LOGGED IN USER (NEW)
# =========================================================
@attendance_bp.route("/api/me", methods=["GET"])
def me():
    employee_id = session.get("employee_id")

    return jsonify({
        "employee_id": employee_id
    })

# =========================================================
# MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/api/mark_attendance", methods=["POST"])
def mark():

    data = request.get_json()

    employee_id = data["employee_id"]
    lat = float(data["latitude"])
    lon = float(data["longitude"])
    action = data["action"]

    # CHECK APPROVED LEAVE
    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT *
        FROM tbl_leaves
        WHERE employee_id = %s
        AND status = 'Approved'
        AND CURDATE() BETWEEN start_date AND end_date
    """, (employee_id,))

    leave = cursor.fetchone()

    if leave and action.lower() == "checkin":
        

        return jsonify({
            "status": "leave",
            "message": "Today is Leave. Check-In Not Allowed."
        }), 400

    

    deputed = get_deputed_location(employee_id)

    if deputed:
        office_lat = float(deputed["latitude"])
        office_lon = float(deputed["longitude"])
        radius = float(deputed["radius"])
    else:
        office = get_employee_location(employee_id)

        if not office:
            return jsonify({
                "status": "error",
                "message": "Office location not assigned"
            }), 400

        office_lat = float(office["latitude"])
        office_lon = float(office["longitude"])
        radius = float(office["radius"])

    print("Employee Lat:", lat)
    print("Employee Lon:", lon)

    print("Office Lat:", office_lat)
    print("Office Lon:", office_lon)

    distance = calculate_distance(
        lat,
        lon,
        office_lat,
        office_lon
    )

    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        INSERT INTO tracking
        (employee_id, latitude, longitude, last_updated)
        VALUES (%s,%s,%s,NOW())
        ON DUPLICATE KEY UPDATE
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            last_updated = NOW()
    """, (
        employee_id,
        lat,
        lon
    ))

    conn.commit()
    cursor.close()

    print("Distance:", distance)
    inside = distance <= radius

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT check_in, check_out
        FROM attendance_master
        WHERE employee_id = %s AND attendance_date = CURDATE()
    """, (employee_id,))

    today = cursor.fetchone()

    

    already_checked_in = False
    already_checked_out = False

    if today:
        already_checked_in = today["check_in"] is not None
        already_checked_out = today["check_out"] is not None

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        UPDATE attendance_master
        SET arrival_status = NULL
        WHERE employee_id = %s
        AND attendance_date = CURDATE()
        AND check_in IS NULL
    """, (employee_id,))

    conn.commit()
    cursor.close()

    msg = mark_attendance(
        employee_id,
        lat,
        lon,
        inside,
        action
    )
    print(msg)

    if msg.get("status") != "success":
        return jsonify(msg)


    return jsonify({
        "status": msg["status"],
        "message": msg["message"],
        "distance": round(distance, 2),
        "inside_geofence": inside,
        "already_checked_in": already_checked_in,
        "already_checked_out": already_checked_out,
    })

# 📊 MONTHLY REPORT (EMPLOYEE WISE)
@attendance_bp.route("/api/attendance_report", methods=["POST"])
def report():

    data = request.get_json()

    print("===== REPORT API CALLED =====")
    print(data)

    employee_id = data["employee_id"]
    month = int(data["month"])   # ✅ FIX
    year = int(data["year"])     # ✅ FIX

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT CONCAT(first_name,' ',last_name) AS full_name
        FROM employees
        WHERE employee_id=%s
    """, (employee_id,))

    employee = cursor.fetchone()

    employee_name = (
        employee["full_name"]
        if employee else ""
    )

    cursor.execute("""
        SELECT COUNT(*) as present
        FROM attendance_master
        WHERE employee_id = %s
        AND MONTH(attendance_date) = %s
        AND YEAR(attendance_date) = %s
        AND status IN ('Present','Late','Full Day')
    """, (employee_id, month, year))
    present = cursor.fetchone()["present"]

    cursor.execute("""
        SELECT COUNT(*) as absent
        FROM attendance_master
        WHERE employee_id = %s
        AND MONTH(attendance_date) = %s
        AND YEAR(attendance_date) = %s
        AND status = 'Absent'
    """, (employee_id, month, year))
    absent = cursor.fetchone()["absent"]

    cursor.execute("""
        SELECT COUNT(*) as half_day
        FROM attendance_master
        WHERE employee_id = %s
        AND MONTH(attendance_date) = %s
        AND YEAR(attendance_date) = %s
        AND status = 'Half Day'
    """, (employee_id, month, year))
    half_day = cursor.fetchone()["half_day"]

    cursor.execute("""
        SELECT COALESCE(SUM(total_days),0) AS leave_count
        FROM tbl_leaves
        WHERE employee_id = %s
        AND status = 'Approved'
        AND MONTH(start_date) = %s
        AND YEAR(start_date) = %s
    """, (employee_id, month, year))

    leave_count = cursor.fetchone()["leave_count"]

    cursor.execute("""
        SELECT COALESCE(SUM(work_hours),0) as total_hours
        FROM attendance_master
        WHERE employee_id = %s
        AND MONTH(attendance_date) = %s
        AND YEAR(attendance_date) = %s
    """, (employee_id, month, year))

    row = cursor.fetchone()
    total_hours = float(row["total_hours"] or 0)


    total_days = present + absent + half_day

    attendance_score = present + (half_day * 0.5)

    percent = (
        attendance_score / total_days * 100
    ) if total_days > 0 else 0

    # ==========================
    # DEBUG PRINTS
    # ==========================
    print("\n========== MONTHLY REPORT ==========")
    print("Employee ID :", employee_id)
    print("Employee Name :", employee_name)
    print("Month :", month)
    print("Year :", year)
    print("Present :", present)
    print("Absent :", absent)
    print("Half Day :", half_day)
    print("Leave :", leave_count)
    print("Total Hours :", total_hours)
    print("Attendance % :", percent)
    print("===================================\n")

    return jsonify({
    "employee_id": employee_id,
    "employee_name": employee_name,
    "month": month,
    "year": year,
    "present": present,
    "absent": absent,
    "half_day": half_day,
    "leave": leave_count,
    "total_work_hours": round(total_hours, 2),
    "attendance_percent": round(percent, 2)
})

# =========================================================
# ADMIN MONTHLY MATRIX REPORT (ATTENDANCE + LEAVE)
# =========================================================
@attendance_bp.route("/api/monthly_matrix_report", methods=["GET"])
def monthly_matrix_report():

    from datetime import datetime

    today = datetime.today()

    month = request.args.get("month", type=int) or today.month
    year = request.args.get("year", type=int) or today.year

    employee_id = request.args.get("employee_id", type=int)

    print("FILTER EMPLOYEE ID =", employee_id)
    print("ALL REQUEST ARGS =", request.args)

    department = request.args.get("department")

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    print("RAW ARGS:", request.args)
    print("EMPLOYEE ID RAW:", request.args.get("employee_id"))

    # =====================================================
    # EMPLOYEES
    # =====================================================
    department = request.args.get("department")

    query = """
        SELECT
            e.employee_id,
            e.employee_code,
            CONCAT(e.first_name,' ',e.last_name) AS full_name,
            d.department_name AS department,
            ds.designation_name AS role

        FROM employees e

        LEFT JOIN tbl_department d
            ON e.department_id=d.department_id

        LEFT JOIN tbl_designation ds
            ON e.designation_id=ds.designation_id

        WHERE e.is_active=1
    """

    params = []

    if employee_id:
        query += " AND e.employee_id=%s"
        params.append(employee_id)

    # Department filter
    if department:
        query += " AND d.department_name=%s"
        params.append(department)

    query += " ORDER BY employee_id"

    cursor.execute(query, tuple(params))

    employees = cursor.fetchall()

    # =====================================================
    # ATTENDANCE
    # =====================================================
    if employee_id:
        cursor.execute("""
            SELECT employee_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND employee_id=%s
        """, (month, year, employee_id))
    else:
        cursor.execute("""
            SELECT employee_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
        """, (month, year))

    attendance_data = cursor.fetchall()

    # =====================================================
    # HOLIDAYS
    # =====================================================
    cursor.execute("""
        SELECT DAY(holiday_date) as day
        FROM holiday_master
        WHERE MONTH(holiday_date)=%s
        AND YEAR(holiday_date)=%s
    """, (month, year))

    holiday_days = [h["day"] for h in cursor.fetchall()]

    # =====================================================
    # LEAVES
    # =====================================================
    if employee_id:
        cursor.execute("""
            SELECT employee_id,
                   start_date,
                   end_date
            FROM tbl_leaves
            WHERE status='Approved'
            AND (
                MONTH(start_date)=%s
                OR MONTH(end_date)=%s
            )
            AND YEAR(start_date)=%s
            AND employee_id=%s
        """, (month, month, year, employee_id))
    else:
        cursor.execute("""
            SELECT employee_id,
                   start_date,
                   end_date
            FROM tbl_leaves
            WHERE status='Approved'
            AND (
                MONTH(start_date)=%s
                OR MONTH(end_date)=%s
            )
            AND YEAR(start_date)=%s
        """, (month, month, year))

    leave_data = cursor.fetchall()

    total_days = calendar.monthrange(year, month)[1]

    report = []

    # =====================================================
    # FIND WEEKLY OFFS
    # =====================================================
    weekly_off_days = []

    saturday_count = 0

    for day in range(1, total_days + 1):

        weekday = calendar.weekday(year, month, day)

        # Sunday
        if weekday == 6:
            weekly_off_days.append(day)

        # Saturday
        elif weekday == 5:

            saturday_count += 1

            # 2nd and 4th Saturday
            if saturday_count in [2, 4]:
                weekly_off_days.append(day)

    # =====================================================
    # BUILD REPORT
    # =====================================================
    for emp in employees:

        attendance_map = {}

        present = 0
        absent = 0
        half_day = 0
        holiday = 0
        leave = 0
        weekly_off = 0

        # =================================================
        # DEFAULT STATUS
        # =================================================
        for day in range(1, total_days + 1):
            key = str(day).zfill(2)
            attendance_map[key] = "-"

         # Apply Holidays
        for d in holiday_days:
            key = str(d).zfill(2)
            attendance_map[key] = "H"

        # Apply Weekly Off
        for d in weekly_off_days:
            key = str(d).zfill(2)

            if attendance_map[key] == "-":
                attendance_map[key] = "WO"

        # =================================================
        # APPLY LEAVE
        # =================================================
        from datetime import timedelta

        for lv in leave_data:

            if lv["employee_id"] != emp["employee_id"]:
                continue

            current = lv["start_date"]

            while current <= lv["end_date"]:

                if current.month == month and current.year == year:

                    key = str(current.day).zfill(2)

                    if attendance_map[key] not in ["H", "WO"]:
                        attendance_map[key] = "L"

                current += timedelta(days=1)
        # =================================================
        # APPLY ATTENDANCE
        # =================================================
        for att in attendance_data:

            if att["employee_id"] == emp["employee_id"]:

                key = str(att["day"]).zfill(2)

                if attendance_map[key] in ["H", "WO"]:
                    continue

                status = att["status"]

                if status in ["Present", "Late", "Full Day"]:
                    attendance_map[key] = "P"

                elif status == "Half Day":
                    attendance_map[key] = "HD"

                elif status == "Absent":
                    attendance_map[key] = "A"

                elif status == "Leave":
                    attendance_map[key] = "L"

                elif status == "Holiday":
                    attendance_map[key] = "H"

                elif status == "Weekly Off":
                    attendance_map[key] = "WO"

        # =================================================
        # COUNTS
        # =================================================
        for value in attendance_map.values():

            if value == "P":
                present += 1

            elif value == "A":
                absent += 1

            elif value == "HD":
                half_day += 1

            elif value == "H":
                holiday += 1

            elif value == "L":
                leave += 1

            elif value == "WO":
                weekly_off += 1

        report.append({
            "employee_id": emp["employee_id"],
            "employee_code": emp["employee_code"],
            "employee_name": emp["full_name"],
            "role": emp["role"],
            "department": emp["department"],
            "attendance": attendance_map,
            "summary": {
                "present": present,
                "absent": absent,
                "half_day": half_day,
                "holiday": holiday,
                "leave": leave,
                "weekly_off": weekly_off
            }
        })

  

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "total_days": total_days,
        "data": report
    })

@attendance_bp.route("/api/get_departments", methods=["GET"])
def get_departments():
    """
    Returns all departments for the Department dropdown.
    """

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    try:
        cursor.execute("""
            SELECT
                department_id,
                department_name
            FROM tbl_department
            ORDER BY department_name ASC
        """)

        departments = cursor.fetchall()

        return jsonify(departments)

    except Exception as e:
        print("GET DEPARTMENTS ERROR:", e)
        return jsonify([]), 500

    finally:
        cursor.close()


from flask import jsonify, request
from datetime import date
import calendar

@attendance_bp.route("/api/monthly_detailed_report", methods=["GET"])
def monthly_detailed_report():

    # =====================================================
    # SAFE PARAM PARSING (IMPORTANT FIX)
    # =====================================================
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    employee_id = request.args.get("employee_id", type=int)
    department = request.args.get("department")

    from datetime import datetime
    today = datetime.today()

    if not month:
        month = today.month
    if not year:
        year = today.year

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)

    # =====================================================
    # EMPLOYEE QUERY
    # =====================================================
    emp_query = """
        SELECT
            e.employee_id,
            CONCAT(e.first_name,' ',e.last_name) AS full_name,
            d.department_name AS department,
            ds.designation_name AS role
        FROM employees e
        LEFT JOIN tbl_department d
            ON e.department_id=d.department_id
        LEFT JOIN tbl_designation ds
            ON e.designation_id=ds.designation_id
        WHERE e.is_active=1
    """

    emp_params = []

    # FIX: proper employee filter
    if employee_id:
        emp_query += " AND e.employee_id=%s"
        emp_params.append(employee_id)

    # FIX: department filter safe
    if department:
        emp_query += " AND d.department_name=%s"
        emp_params.append(department)

    cursor.execute(emp_query, tuple(emp_params))
    employees = cursor.fetchall()

    if not employees:
        return jsonify({
            "success": True,
            "month": month,
            "year": year,
            "data": []
        })

    employee_ids = [e["employee_id"] for e in employees]

    # =====================================================
    # FIX: avoid IN () crash
    # =====================================================
    attendance_rows = []

    if employee_ids:

        attendance_query = f"""
            SELECT
                employee_id,
                DATE(attendance_date) AS attendance_date,
                check_in,
                check_out,
                work_hours,
                status,
                arrival_status,
                checkout_type
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND employee_id IN ({','.join(['%s'] * len(employee_ids))})
            ORDER BY attendance_date ASC
        """

        cursor.execute(attendance_query, tuple([month, year] + employee_ids))
        attendance_rows = cursor.fetchall()

    # =====================================================
    # HOLIDAYS
    # =====================================================
    cursor.execute("""
        SELECT holiday_date
        FROM holiday_master
        WHERE MONTH(holiday_date)=%s
        AND YEAR(holiday_date)=%s
    """, (month, year))

    holiday_dates = {row["holiday_date"] for row in cursor.fetchall()}

    # =====================================================
    # LEAVES
    # =====================================================
    cursor.execute("""
        SELECT employee_id, start_date, end_date
        FROM tbl_leaves
        WHERE status='Approved'
    """)

    leave_rows = cursor.fetchall()

    # =====================================================
    # MAP ATTENDANCE
    # =====================================================
    attendance_map = {}

    for row in attendance_rows:
        key = (row["employee_id"], row["attendance_date"])
        attendance_map[key] = row

    # =====================================================
    # MONTH LIMIT
    # =====================================================
    total_days = calendar.monthrange(year, month)[1]
    today = date.today()

    max_day = total_days
    if month == today.month and year == today.year:
        max_day = today.day

    # =====================================================
    # BUILD RESULT
    # =====================================================
    result = []

    for emp in employees:

        records = []
        saturday_count = 0

        for day in range(1, max_day + 1):

            current_date = date(year, month, day)
            weekday = current_date.weekday()

            is_weekly_off = False

            if weekday == 6:
                is_weekly_off = True

            elif weekday == 5:
                saturday_count += 1
                if saturday_count in [2, 4]:
                    is_weekly_off = True

            key = (emp["employee_id"], current_date)
            attendance = attendance_map.get(key)

            status = "-"
            check_in = "-"
            check_out = "-"
            hours = "-"
            arrival = "-"
            checkout_type = "-"

            # =============================
            # ATTENDANCE
            # =============================
            if attendance:

                status = attendance["status"] or "Present"

                check_in = attendance["check_in"].strftime("%I:%M %p") if attendance["check_in"] else "-"
                check_out = attendance["check_out"].strftime("%I:%M %p") if attendance["check_out"] else "-"
                hours = attendance["work_hours"] or "-"
                arrival = attendance["arrival_status"] or "-"
                checkout_type = attendance["checkout_type"] or "-"

            # =============================
            # HOLIDAY
            # =============================
            elif current_date in holiday_dates:
                status = "Holiday"

            # =============================
            # LEAVE / WEEKOFF
            # =============================
            else:

                for lv in leave_rows:
                    if lv["employee_id"] != emp["employee_id"]:
                        continue

                    if lv["start_date"] <= current_date <= lv["end_date"]:
                        status = "Leave"
                        break

                if status == "-" and is_weekly_off:
                    status = "Weekly Off"

            records.append({
                "date": current_date.strftime("%d-%m-%Y"),
                "check_in": check_in,
                "check_out": check_out,
                "hours": str(hours),
                "status": status,
                "arrival": arrival,
                "checkout_type": checkout_type
            })

        result.append({
            "employee_id": emp["employee_id"],
            "employee_name": emp["full_name"],
            "role": emp["role"],
            "department": emp["department"],
            "records": records
        })

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "data": result
    })
# =========================================================
# DOWNLOAD MONTHLY REPORT PDF
# =========================================================
import pdfkit

@attendance_bp.route("/api/download_monthly_report_pdf", methods=["GET"])
def download_pdf():

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    # ===============================
    # VALIDATION (VERY IMPORTANT)
    # ===============================
    if not month or not year:
        return jsonify({
            "success": False,
            "message": "Month and Year are required"
        }), 400

    employee_id = request.args.get("employee_id")
    department = request.args.get("department")

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    # =====================================================
    # EMPLOYEES
    # =====================================================
    query = """
        SELECT
            e.employee_id,
            e.employee_code,
            CONCAT(e.first_name,' ',e.last_name) AS full_name,
            d.department_name AS department,
            ds.designation_name AS role

        FROM employees e

        LEFT JOIN tbl_department d
            ON e.department_id=d.department_id

        LEFT JOIN tbl_designation ds
            ON e.designation_id=ds.designation_id

        WHERE e.is_active=1
    """

    params = []

    if employee_id:
        query += " AND e.employee_id=%s"
        params.append(employee_id)

    if department:
        query += " AND d.department_name=%s"
        params.append(department)

    query += " ORDER BY employee_id"

    cursor.execute(query, tuple(params))

    employees = cursor.fetchall()

    # =====================================================
    # LEAVE DATA (MOVE HERE - BEFORE EMPLOYEE LOOP)
    # =====================================================
    cursor.execute("""
        SELECT employee_id, start_date, end_date
        FROM tbl_leaves
        WHERE status='Approved'
        AND (
            MONTH(start_date)=%s
            OR MONTH(end_date)=%s
        )
        AND YEAR(start_date)=%s
    """, (month, month, year))

    leave_data_all = cursor.fetchall()   

    # =====================================================
    # ATTENDANCE
    # =====================================================
    if employee_id:
        cursor.execute("""
            SELECT employee_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND employee_id=%s
        """, (month, year, employee_id))
    else:
        cursor.execute("""
            SELECT employee_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
        """, (month, year))

    attendance_data = cursor.fetchall()

    # =====================================================
    # HOLIDAYS
    # =====================================================
    cursor.execute("""
        SELECT DAY(holiday_date) as day
        FROM holiday_master
        WHERE MONTH(holiday_date)=%s
        AND YEAR(holiday_date)=%s
    """, (month, year))

    holiday_days = [h["day"] for h in cursor.fetchall()]

    total_days = calendar.monthrange(year, month)[1]

    # =====================================================
    # WEEKLY OFFS
    # =====================================================
    weekly_off_days = []

    saturday_count = 0

    for day in range(1, total_days + 1):

        weekday = calendar.weekday(year, month, day)

        # Sunday
        if weekday == 6:
            weekly_off_days.append(day)

        # 2nd & 4th Saturday
        elif weekday == 5:

            saturday_count += 1

            if saturday_count in [2, 4]:
                weekly_off_days.append(day)

    month_name = calendar.month_name[month]

    # =====================================================
    # COMPANY TOTAL COUNTS
    # =====================================================
    grand_present = 0
    grand_absent = 0
    grand_half_day = 0
    grand_leave = 0
    grand_holiday = 0
    grand_weekly_off = 0

    # =====================================================
    # HTML START
    # =====================================================
    html = f"""
    <html>

    <head>

    <style>

        body {{
            font-family: Arial, sans-serif;
            padding: 15px;
        }}

        .title {{
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #1e3a8a;
        }}

        .legend {{
            margin-bottom: 15px;
            padding: 10px;
            background: #eef4ff;
            border-left: 5px solid #2563eb;
            font-size: 12px;
            line-height: 24px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
        }}

        th {{
            background: #dbeafe;
            border: 1px solid #cbd5e1;
            padding: 7px;
            font-size: 10px;
        }}

        td {{
            border: 1px solid #e5e7eb;
            text-align: center;
            padding: 7px;
            font-size: 10px;
            font-weight: bold;
        }}

        .main-header {{
            background: #1e3a8a;
            color: white;
            font-size: 12px;
        }}

        .code {{
            min-width: 100px;
            background: #f9fafb;
        }}

        .name {{
            text-align: left;
            min-width: 250px;
            background: #f9fafb;
            padding: 10px;
        }}

        .P {{
            background: #22c7b8;
            color: white;
        }}

        .A {{
            background: #ff6b57;
            color: white;
        }}

        .HD {{
            background: #2f73c9;
            color: white;
        }}

        .H {{
            background: #f7c500;
            color: black;
        }}

        .L {{
            background: #ff7f3f;
            color: white;
        }}

        .WO {{
            background: #404040;
            color: white;
        }}

        .dash {{
            background: #ffffff;
            color: #555;
        }}

        .day-header {{
            background: #eff6ff;
            font-size: 9px;
            font-weight: bold;
        }}

        .sunday {{
            background: #fecaca;
        }}

        .saturday {{
            background: #fde68a;
        }}

        .company-summary {{
            margin-top: 25px;
        }}

        .company-summary th {{
            background: #1e3a8a;
            color: white;
            font-size: 12px;
        }}

        .company-summary td {{
            background: #f9fafb;
            font-size: 12px;
            padding: 12px;
        }}

    </style>

    </head>

    <body>

        <div class="title">
            MONTHLY ATTENDANCE MATRIX REPORT
        </div>

        <div class="legend">

            <b>REPORT FOR :</b>
            {month_name.upper()} {year}

            <br><br>

            P = Present |
            A = Absent |
            HD = Half Day |
            H = Holiday |
            L = Approved Leave |
            WO = Weekly Off

        </div>

        <table>

            <tr>

                <th colspan="{total_days + 2}"
                    class="main-header">

                    REPORT FOR :
                    {month_name.upper()} {year}

                </th>

            </tr>

            <!-- DAY NAME ROW -->

            <tr>

                <th rowspan="2" style="width:120px">
                    EMP ID
                </th>

                <th rowspan="2" style="width:260px">
                    EMPLOYEE DETAILS
                </th>
    """

    # =====================================================
    # DAY NAME HEADER
    # =====================================================
    for i in range(1, total_days + 1):

        day_name = datetime(year, month, i).strftime("%a")

        cls = ""

        if day_name == "Sun":
            cls = "sunday"

        elif day_name == "Sat":
            cls = "saturday"

        html += f"""
            <th class="day-header {cls}">
                {day_name}
            </th>
        """

    html += "</tr>"

    # =====================================================
    # DATE HEADER
    # =====================================================
    html += "<tr>"

    for i in range(1, total_days + 1):

        html += f"""
            <th>
                {i}
            </th>
        """

    html += "</tr>"


    # =================================================
    # EMPLOYEE LOOP
    # =================================================
    for emp in employees:

        attendance_map = {}

        present = 0
        absent = 0
        half_day = 0
        holiday = 0
        leave = 0
        weekly_off = 0

        # =================================================
        # 1. DEFAULT
        # =================================================
        for d in range(1, total_days + 1):
            key = str(d).zfill(2)
            attendance_map[key] = "-"

        # =================================================
        # 2. HOLIDAY (H)
        # =================================================
        for d in holiday_days:
            key = str(d).zfill(2)
            attendance_map[key] = "H"

        # =================================================
        # 3. WEEKLY OFF (WO)
        # =================================================
        for d in weekly_off_days:
            key = str(d).zfill(2)
            if attendance_map[key] == "-":
                attendance_map[key] = "WO"

        # =================================================
        # 4. LEAVE (L)  [HIGHEST PRIORITY AFTER H & WO]
        # =================================================
        for lv in leave_data_all:

            if lv["employee_id"] != emp["employee_id"]:
                continue

            current = lv["start_date"]

            while current <= lv["end_date"]:

                if current.month == month and current.year == year:

                    key = str(current.day).zfill(2)

                    if attendance_map[key] not in ["H", "WO"]:
                        attendance_map[key] = "L"

                current += timedelta(days=1)

        # =================================================
        # 5. ATTENDANCE (P / A / HD)
        # =================================================
        for att in attendance_data:

            if att["employee_id"] == emp["employee_id"]:

                key = str(att["day"]).zfill(2)

                # DO NOT override priority days
                if attendance_map[key] in ["H", "WO", "L"]:
                    continue

                status = att["status"]

                if status in ["Present", "Late", "Full Day"]:
                    attendance_map[key] = "P"

                elif status == "Half Day":
                    attendance_map[key] = "HD"

                elif status == "Absent":
                    attendance_map[key] = "A"

                elif status == "Leave":
                    attendance_map[key] = "L"
        # =================================================
        # COUNTS
        # =================================================
        for value in attendance_map.values():

            if value == "P":
                present += 1

            elif value == "A":
                absent += 1

            elif value == "HD":
                half_day += 1

            elif value == "H":
                holiday += 1

            elif value == "L":
                leave += 1

            elif value == "WO":
                weekly_off += 1

        # =================================================
        # GRAND TOTALS
        # =================================================
        grand_present += present
        grand_absent += absent
        grand_half_day += half_day
        grand_leave += leave
        grand_holiday += holiday
        grand_weekly_off += weekly_off

        # =================================================
        # EMPLOYEE ROW
        # =================================================
        html += f"""

        <tr>

            <td class="code">
                {emp['employee_id']}
            </td>

            <td class="name">

                <div style="
                    font-size:16px;
                    font-weight:bold;
                    margin-bottom:6px;
                ">
                    {emp['full_name']}
                </div>

                <div style="
                    font-size:11px;
                    color:#4b5563;
                    margin-bottom:4px;
                ">
                    {emp['role'] or '-'}
                </div>

                <div style="
                    font-size:11px;
                    color:#2563eb;
                ">
                    {emp['department'] or '-'}
                </div>

            </td>
        """

        # =================================================
        # DAILY CELLS
        # =================================================
        for i in range(1, total_days + 1):

            key = str(i).zfill(2)

            val = attendance_map[key]

            today = datetime.now()

            final_val = val

            # Future month/year
            if (
                year > today.year or
                (
                    year == today.year and
                    month > today.month
                )
            ):
                final_val = "-"

            # Current month logic
            elif (
                year == today.year and
                month == today.month
            ):

                # Future dates
                if i > today.day:

                    final_val = "-"

                # Today's attendance before 6 PM
                elif i == today.day:

                    if today.hour < 19:

                        final_val = "-"

            cell_class = final_val if final_val != "-" else "dash"

            html += f"""
                <td class="{cell_class}">
                    {final_val}
                </td>
            """

        html += "</tr>"

        # =================================================
        # TOTALS ROW
        # =================================================
        html += f"""

        <tr>

            <td colspan="2"
                style="
                    background:#e5e7eb;
                    font-weight:bold;
                    color:#1e3a8a;
                    text-align:center;
                    padding:10px;
                ">

                REPORT TOTALS

            </td>

            <td colspan="{total_days}"
                style="
                    text-align:left;
                    padding:10px;
                    background:#f9fafb;
                    font-size:11px;
                ">

                <span style="margin-right:20px;">
                    Present: <b>{present}</b>
                </span>

                <span style="margin-right:20px;">
                    Absent: <b>{absent}</b>
                </span>

                <span style="margin-right:20px;">
                    Half Day: <b>{half_day}</b>
                </span>

                <span style="margin-right:20px;">
                    Leave: <b>{leave}</b>
                </span>

                <span style="margin-right:20px;">
                    Holiday: <b>{holiday}</b>
                </span>

                <span style="margin-right:20px;">
                    WO: <b>{weekly_off}</b>
                </span>

            </td>

        </tr>
        """

    # =====================================================
    # CLOSE MAIN TABLE
    # =====================================================
    html += "</table>"

    html += """

            </body>
            </html>
        """

    # =====================================================
    # PDF GENERATION
    # =====================================================
    path_wkhtmltopdf = r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"

    config = pdfkit.configuration(
        wkhtmltopdf=path_wkhtmltopdf
    )

    options = {
        'page-size': 'A3',
        'orientation': 'Landscape',
        'encoding': "UTF-8",
        'enable-local-file-access': None
    }

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"

    response.headers["Content-Disposition"] = (
        f"attachment; filename=attendance_matrix_{month}_{year}.pdf"
    )


    return response

@attendance_bp.route("/api/download_detailed_report_pdf", methods=["GET"])
def download_detailed_pdf():

    from flask import make_response
    from datetime import date, datetime
    import calendar
    import pdfkit

    # ==========================================
    # FILTERS
    # ==========================================
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    employee_id = request.args.get("employee_id", type=int)
    department = request.args.get("department", default="", type=str)

    today = datetime.today()

    if not month:
        month = today.month

    if not year:
        year = today.year

    conn = mysql.connection

    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)

    # ==========================================
    # EMPLOYEE QUERY
    # ==========================================

    query = """
        SELECT

            e.employee_id,

            CONCAT(e.first_name,' ',e.last_name) AS full_name,

            d.department_name AS department,

            ds.designation_name AS role

        FROM employees e

        LEFT JOIN tbl_department d
            ON e.department_id=d.department_id

        LEFT JOIN tbl_designation ds
            ON e.designation_id=ds.designation_id

        WHERE e.is_active=1
    """

    params = []

    if employee_id is not None:
        query += " AND e.employee_id=%s"
        params.append(employee_id)

    if department:
        query += " AND d.department_name=%s"
        params.append(department)

    query += " ORDER BY e.employee_id"

    cursor.execute(query, tuple(params))

    employees = cursor.fetchall()

    if not employees:
        return "No Data Found"

    # ==========================================
    # EMPLOYEE IDS
    # ==========================================

    employee_ids = [emp["employee_id"] for emp in employees]

    # ==========================================
    # ATTENDANCE
    # ==========================================

    attendance_query = f"""
        SELECT

            employee_id,

            DATE(attendance_date) AS attendance_date,

            check_in,

            check_out,

            work_hours,

            status,

            arrival_status,

            checkout_type

        FROM attendance_master

        WHERE MONTH(attendance_date)=%s
        AND YEAR(attendance_date)=%s
        AND employee_id IN ({','.join(['%s'] * len(employee_ids))})

        ORDER BY attendance_date
    """

    cursor.execute(
        attendance_query,
        tuple([month, year] + employee_ids)
    )

    attendance_rows = cursor.fetchall()

    # ==========================================
    # HOLIDAYS
    # ==========================================

    cursor.execute("""
        SELECT holiday_date

        FROM holiday_master

        WHERE MONTH(holiday_date)=%s
        AND YEAR(holiday_date)=%s
    """, (month, year))

    holiday_dates = {
        row["holiday_date"]
        for row in cursor.fetchall()
    }

    # ==========================================
    # APPROVED LEAVES
    # ==========================================

    cursor.execute("""
        SELECT

            employee_id,

            start_date,

            end_date

        FROM tbl_leaves

        WHERE status='Approved'
    """)

    leave_rows = cursor.fetchall()

    # ==========================================
    # ATTENDANCE MAP
    # ==========================================

    attendance_map = {}

    for row in attendance_rows:

        attendance_map[
            (
                row["employee_id"],
                row["attendance_date"]
            )
        ] = row

    # ==========================================
    # BUILD HTML
    # ==========================================

    html = f"""

    <html>

    <head>

    <style>

    body{{

        font-family:Arial;

        padding:20px;

        font-size:12px;

    }}

    h1{{

        text-align:center;

        color:#1e3a8a;

        margin-bottom:25px;

    }}

    h2{{

        background:#eef4ff;

        padding:10px;

        border-left:5px solid #1e3a8a;

    }}

    table{{

        width:100%;

        border-collapse:collapse;

        margin-bottom:35px;

    }}

    th{{

        background:#1e3a8a;

        color:white;

        padding:8px;

        border:1px solid #ccc;

    }}

    td{{

        border:1px solid #ddd;

        padding:7px;

        text-align:center;

    }}

    .Present{{

        color:#16a34a;

        font-weight:bold;

    }}

    .Absent{{

        color:#dc2626;

        font-weight:bold;

    }}

    .HalfDay{{

        color:#2563eb;

        font-weight:bold;

    }}

    .Leave{{

        color:#9333ea;

        font-weight:bold;

    }}

    .Holiday{{

        color:#d97706;

        font-weight:bold;

    }}

    .WeeklyOff{{

        color:#374151;

        font-weight:bold;

    }}

    .summary{{

        background:#f8fafc;

        font-weight:bold;

    }}

    </style>

    </head>

    <body>

    <h1>DETAILED ATTENDANCE REPORT</h1>

    <h3 style="
    text-align:center;
    color:#374151;
    margin-bottom:25px;
    ">
    REPORT FOR: {calendar.month_name[month].upper()} {year}
    </h3>

    

    """

    # ==========================================
    # EMPLOYEE LOOP
    # ==========================================

    total_days = calendar.monthrange(year, month)[1]

    for emp in employees:

        html += f"""

        <h2>

            Employee : {emp['full_name']}

            &nbsp;&nbsp;&nbsp;

            ID : {emp['employee_id']}

            &nbsp;&nbsp;&nbsp;

            Department : {emp['department']}

            &nbsp;&nbsp;&nbsp;

            Designation : {emp['role']}

        </h2>

        <table>

        <tr>

            <th>Date</th>

            <th>Check In</th>

            <th>Check Out</th>

            <th>Work Hours</th>

            <th>Arrival</th>

            <th>Checkout Type</th>

            <th>Status</th>

        </tr>

        """

        present = 0
        absent = 0
        half_day = 0
        leave = 0
        holiday = 0
        weekly_off = 0

        saturday_count = 0

        for day in range(1, total_days + 1):

            current_date = date(year, month, day)

            weekday = current_date.weekday()

            is_weekly_off = False

            if weekday == 6:

                is_weekly_off = True

            elif weekday == 5:

                saturday_count += 1

                if saturday_count in [2, 4]:

                    is_weekly_off = True

            attendance = attendance_map.get(
                (emp["employee_id"], current_date)
            )

            status = "-"
            check_in = "-"
            check_out = "-"
            work_hours = "-"
            arrival = "-"
            checkout_type = "-"

            # ==================================
            # ATTENDANCE FOUND
            # ==================================

            if attendance:

                status = attendance["status"] or "Present"

                if attendance["check_in"]:
                    check_in = attendance["check_in"].strftime("%I:%M %p")

                if attendance["check_out"]:
                    check_out = attendance["check_out"].strftime("%I:%M %p")

                work_hours = attendance["work_hours"] or "-"

                arrival = attendance["arrival_status"] or "-"

                checkout_type = attendance["checkout_type"] or "-"

            # ==================================
            # HOLIDAY
            # ==================================

            elif current_date in holiday_dates:

                status = "Holiday"

            # ==================================
            # LEAVE
            # ==================================

            else:

                for lv in leave_rows:

                    if lv["employee_id"] != emp["employee_id"]:
                        continue

                    if lv["start_date"] <= current_date <= lv["end_date"]:

                        status = "Leave"

                        break

                if status == "-" and is_weekly_off:

                    status = "Weekly Off"

            # ==================================
            # SUMMARY COUNTS
            # ==================================

            if status == "Present":
                present += 1

            elif status == "Absent":
                absent += 1

            elif status == "Half Day":
                half_day += 1

            elif status == "Leave":
                leave += 1

            elif status == "Holiday":
                holiday += 1

            elif status == "Weekly Off":
                weekly_off += 1

            css = status.replace(" ", "")

            # ==================================
            # SPECIAL ROWS
            # ==================================

            if status in ["Holiday", "Leave", "Weekly Off"]:

                html += f"""

                <tr>

                    <td>

                        {current_date.strftime('%d-%m-%Y')}

                    </td>

                    <td colspan="6"

                        class="{css}"

                        style="font-weight:bold;">

                        {status}

                    </td>

                </tr>

                """

            else:

                html += f"""

                <tr>

                    <td>{current_date.strftime('%d-%m-%Y')}</td>

                    <td>{check_in}</td>

                    <td>{check_out}</td>

                    <td>{work_hours}</td>

                    <td>{arrival}</td>

                    <td>{checkout_type}</td>

                    <td class="{css}">

                        {status}

                    </td>

                </tr>

                """

        # ==================================
        # SUMMARY
        # ==================================

        html += f"""

        <tr class="summary">

            <td colspan="7">

                Present : {present}

                &nbsp;&nbsp;&nbsp;&nbsp;

                Absent : {absent}

                &nbsp;&nbsp;&nbsp;&nbsp;

                Half Day : {half_day}

                &nbsp;&nbsp;&nbsp;&nbsp;

                Leave : {leave}

                &nbsp;&nbsp;&nbsp;&nbsp;

                Holiday : {holiday}

                &nbsp;&nbsp;&nbsp;&nbsp;

                Weekly Off : {weekly_off}

            </td>

        </tr>

        </table>

        <br><br>

        """
            # ==========================================
    # CLOSE HTML
    # ==========================================

    html += """

    </body>

    </html>

    """

    cursor.close()

    # ==========================================
    # PDF CONFIG
    # ==========================================

    path_wkhtmltopdf = (
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    config = pdfkit.configuration(
        wkhtmltopdf=path_wkhtmltopdf
    )

    options = {

        "page-size": "A3",

        "orientation": "Landscape",

        "encoding": "UTF-8",

        "margin-top": "10mm",

        "margin-bottom": "10mm",

        "margin-left": "8mm",

        "margin-right": "8mm",

        "enable-local-file-access": None,

        "footer-right": "[page] / [topage]",

        "footer-font-size": "8",

        "footer-spacing": "5",

        "quiet": ""

    }

    # ==========================================
    # GENERATE PDF
    # ==========================================

    pdf = pdfkit.from_string(

        html,

        False,

        configuration=config,

        options=options

    )

    # ==========================================
    # RESPONSE
    # ==========================================

    filename = (
        f"detailed_attendance_report_{month}_{year}.pdf"
    )

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"

    response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}"
    )

    return response

@attendance_bp.route('/monthly-report')
def monthly_report():
    return render_template('monthly_report.html')


@attendance_bp.route("/api/attendance_history", methods=["GET"])
def attendance_history():

    employee_id = request.args.get("employee_id")

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            attendance_date,
            check_in,
            check_out,
            work_hours,
            overtime_minutes,
            status,
            arrival_status,
            checkout_type
        FROM attendance_master
        WHERE employee_id = %s
        AND attendance_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        ORDER BY attendance_date DESC
    """, (employee_id,))

    data = cursor.fetchall()



    return jsonify({
        "status": "success",
        "data": data
    })  