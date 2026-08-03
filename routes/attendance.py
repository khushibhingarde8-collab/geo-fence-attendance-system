from flask import Blueprint, request, jsonify, render_template, session

from database import (
    get_employee_location,
    get_deputed_location,
    mark_attendance,
    get_connection
)
from utils import calculate_distance
from utils import calculate_attendance_status
import calendar

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import io


import pdfkit
from flask import make_response

attendance_bp = Blueprint("attendance_bp", __name__)


# =========================================================
# GET LOGGED IN USER (NEW)
# =========================================================
@attendance_bp.route("/api/me", methods=["GET"])
def me():
    emp_id = session.get("emp_id")
    return jsonify({"emp_id": emp_id})


# =========================================================
# MARK ATTENDANCE
# =========================================================
@attendance_bp.route("/api/mark_attendance", methods=["POST"])
def mark():

    data = request.get_json()

    emp_id = data["emp_id"]
    lat = float(data["latitude"])
    lon = float(data["longitude"])
    action = data["action"]

    deputed = get_deputed_location(emp_id)

    if deputed:
        office_lat = float(deputed["latitude"])
        office_lon = float(deputed["longitude"])
        radius = float(deputed["radius"])
    else:
        office = get_employee_location(emp_id)
        office_lat = float(office["latitude"])
        office_lon = float(office["longitude"])
        radius = float(office["radius"])

    distance = calculate_distance(lat, lon, office_lat, office_lon)
    inside = distance <= radius

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT check_in, check_out
        FROM attendance_master
        WHERE emp_id = %s AND attendance_date = CURDATE()
    """, (emp_id,))

    today = cursor.fetchone()

    already_checked_in = False
    already_checked_out = False

    if today:
        already_checked_in = today["check_in"] is not None
        already_checked_out = today["check_out"] is not None

    msg = mark_attendance(emp_id, lat, lon, inside, action)

    final_status = calculate_attendance_status(emp_id)

    cursor.execute("""
        UPDATE attendance_master
        SET status = %s
        WHERE emp_id = %s AND attendance_date = CURDATE()
    """, (final_status, emp_id))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": msg,
        "distance": round(distance, 2),
        "inside_geofence": inside,
        "already_checked_in": already_checked_in,
        "already_checked_out": already_checked_out,
        "final_status": final_status
    })


# =========================================================
# ADMIN MONTHLY MATRIX REPORT (ATTENDANCE + LEAVE)
# =========================================================
@attendance_bp.route("/api/monthly_matrix_report", methods=["GET"])
def monthly_matrix_report():

    month = int(request.args.get("month"))
    year = int(request.args.get("year"))

    emp_id = request.args.get("emp_id")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # =====================================================
    # EMPLOYEES
    # =====================================================
    department = request.args.get("department")

    query = """
        SELECT emp_id,
            emp_code,
            full_name,
            role,
            department
        FROM employees
        WHERE status='Active'
    """

    params = []

    # Employee filter
    if emp_id:
        query += " AND emp_id=%s"
        params.append(emp_id)

    # Department filter
    if department:
        query += " AND department=%s"
        params.append(department)

    query += " ORDER BY emp_id"

    cursor.execute(query, tuple(params))

    employees = cursor.fetchall()

    # =====================================================
    # ATTENDANCE
    # =====================================================
    if emp_id:
        cursor.execute("""
            SELECT emp_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND emp_id=%s
        """, (month, year, emp_id))
    else:
        cursor.execute("""
            SELECT emp_id,
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
    if emp_id:
        cursor.execute("""
            SELECT emp_id,
                   from_date,
                   to_date
            FROM leave_requests
            WHERE status='Approved'
            AND (
                MONTH(from_date)=%s
                OR MONTH(to_date)=%s
            )
            AND YEAR(from_date)=%s
            AND emp_id=%s
        """, (month, month, year, emp_id))
    else:
        cursor.execute("""
            SELECT emp_id,
                   from_date,
                   to_date
            FROM leave_requests
            WHERE status='Approved'
            AND (
                MONTH(from_date)=%s
                OR MONTH(to_date)=%s
            )
            AND YEAR(from_date)=%s
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

            if day in holiday_days:
                attendance_map[key] = "H"

            elif day in weekly_off_days:
                attendance_map[key] = "WO"

            else:
                attendance_map[key] = "A"

        # =================================================
        # APPLY LEAVE
        # =================================================
        for lv in leave_data:

            if lv["emp_id"] == emp["emp_id"]:

                from_day = lv["from_date"].day
                to_day = lv["to_date"].day

                for d in range(from_day, to_day + 1):

                    if d > total_days:
                        continue

                    key = str(d).zfill(2)

                    if attendance_map[key] in ["H", "WO"]:
                        continue

                    attendance_map[key] = "L"

        # =================================================
        # APPLY ATTENDANCE
        # =================================================
        for att in attendance_data:

            if att["emp_id"] == emp["emp_id"]:

                key = str(att["day"]).zfill(2)

                if attendance_map[key] in ["H", "WO"]:
                    continue

                status = att["status"]

                if status in ["Present", "Full Day"]:
                    attendance_map[key] = "P"

                elif status == "Half Day":
                    attendance_map[key] = "HD"

                elif status == "Absent":
                    attendance_map[key] = "A"

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
            "emp_id": emp["emp_id"],
            "emp_code": emp["emp_code"],
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

    conn.close()

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "total_days": total_days,
        "data": report
    })

@attendance_bp.route("/api/get_departments", methods=["GET"])
def get_departments():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT DISTINCT department
        FROM employees
        WHERE department IS NOT NULL
        AND department != ''
        ORDER BY department
    """)

    data = cursor.fetchall()

    conn.close()

    return jsonify(data)

# =========================================================
# DOWNLOAD MONTHLY REPORT PDF
# =========================================================
from datetime import datetime
import calendar
import pdfkit

@attendance_bp.route("/api/download_monthly_report_pdf", methods=["GET"])
def download_pdf():

    month = int(request.args.get("month"))
    year = int(request.args.get("year"))
    emp_id = request.args.get("emp_id")
    department = request.args.get("department")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # =====================================================
    # EMPLOYEES
    # =====================================================
    query = """
        SELECT emp_id,
            emp_code,
            full_name,
            role,
            department
        FROM employees
        WHERE status='Active'
    """

    params = []

    if emp_id:
        query += " AND emp_id=%s"
        params.append(emp_id)

    if department:
        query += " AND department=%s"
        params.append(department)

    query += " ORDER BY emp_id"

    cursor.execute(query, tuple(params))

    employees = cursor.fetchall()

    # =====================================================
    # ATTENDANCE
    # =====================================================
    if emp_id:
        cursor.execute("""
            SELECT emp_id,
                   DAY(attendance_date) as day,
                   status
            FROM attendance_master
            WHERE MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND emp_id=%s
        """, (month, year, emp_id))
    else:
        cursor.execute("""
            SELECT emp_id,
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

    # =====================================================
    # EMPLOYEE LOOP
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
        for d in range(1, total_days + 1):

            key = str(d).zfill(2)

            if d in holiday_days:

                attendance_map[key] = "H"

            elif d in weekly_off_days:

                attendance_map[key] = "WO"

            else:

                attendance_map[key] = "A"

        # =================================================
        # LEAVES
        # =================================================
        cursor.execute("""
            SELECT from_date, to_date
            FROM leave_requests
            WHERE emp_id=%s
            AND status='Approved'
            AND (
                MONTH(from_date)=%s
                OR MONTH(to_date)=%s
            )
            AND YEAR(from_date)=%s
        """, (emp["emp_id"], month, month, year))

        leave_data = cursor.fetchall()

        for lv in leave_data:

            start_day = lv["from_date"].day
            end_day = lv["to_date"].day

            for d in range(start_day, end_day + 1):

                if d > total_days:
                    continue

                key = str(d).zfill(2)

                if attendance_map[key] not in ["H", "WO"]:

                    attendance_map[key] = "L"

        # =================================================
        # ATTENDANCE
        # =================================================
        for att in attendance_data:

            if att["emp_id"] == emp["emp_id"]:

                key = str(att["day"]).zfill(2)

                if attendance_map[key] in ["H", "WO"]:
                    continue

                if att["status"] in ["Present", "Full Day"]:

                    attendance_map[key] = "P"

                elif att["status"] == "Half Day":

                    attendance_map[key] = "HD"

                elif att["status"] == "Absent":

                    attendance_map[key] = "A"

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
                {emp['emp_id']}
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

                    if today.hour < 18:

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

    conn.close()

    return response

@attendance_bp.route('/monthly-report')
def monthly_report():
    return render_template('monthly_report.html')