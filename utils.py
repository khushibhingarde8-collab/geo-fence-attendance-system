import math
import os
import smtplib

from datetime import datetime
from email.mime.text import MIMEText

from config import init_mysql, mysql



# =========================================================
# DISTANCE CALCULATION
# =========================================================
def calculate_distance(lat1, lon1, lat2, lon2):

    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        R = 6371000  # meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)

        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1)
            * math.cos(phi2)
            * math.sin(dlambda / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return round(R * c, 2)

    except Exception as e:
        print("Distance Error:", e)
        return 0.0


# =========================================================
# CONFIG
# =========================================================
LATE_TIME = datetime.strptime("10:00:00", "%H:%M:%S").time()


# =========================================================
# SECOND / FOURTH SATURDAY CHECK
# =========================================================
def is_second_or_fourth_saturday(date):

    if date.weekday() != 5:
        return False

    week_number = (date.day - 1) // 7 + 1

    return week_number in [2, 4]


# =========================================================
# ATTENDANCE STATUS
# =========================================================
def calculate_attendance_status(employee_id):

    cur = mysql.connection.cursor()

    today = datetime.now().date()

    # -----------------------------------------------------
    # HOLIDAY CHECK
    # -----------------------------------------------------
    cur.execute("""
        SELECT 1
        FROM holiday_master
        WHERE holiday_date = %s
    """, (today,))

    is_holiday = (
        cur.fetchone()
        or today.weekday() == 6
        or is_second_or_fourth_saturday(today)
    )

    if is_holiday:
        cur.close()
        return "Holiday"

    # -----------------------------------------------------
    # FETCH ATTENDANCE
    # -----------------------------------------------------
    cur.execute("""
        SELECT check_in, check_out, work_hours
        FROM attendance_master
        WHERE employee_id = %s
        AND attendance_date = CURDATE()
    """, (employee_id,))

    row = cur.fetchone()

    cur.close()

    # -----------------------------------------------------
    # ABSENT
    # -----------------------------------------------------
    if not row or not row["check_in"]:
        return "Absent"

    check_in = row["check_in"]
    work_hours = row["work_hours"] or 0

    # -----------------------------------------------------
    # LATE
    # -----------------------------------------------------
    if check_in.time() > LATE_TIME:
        return "Late"

    # -----------------------------------------------------
    # FULL DAY
    # -----------------------------------------------------
    if work_hours >= 8:
        return "Full Day"

    # -----------------------------------------------------
    # HALF DAY
    # -----------------------------------------------------
    if work_hours > 0:
        return "Half Day"

    return "Absent"


# =========================================================
# EMAIL SENDER
# =========================================================
def send_email(to_email, subject, body):

    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("Email credentials missing")
        return

    msg = MIMEText(body, "html")

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)

        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(
            sender_email,
            to_email,
            msg.as_string()
        )

        server.quit()

        print("Email sent successfully")

    except Exception as e:
        print("Email Error:", e)