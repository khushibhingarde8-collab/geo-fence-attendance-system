import mysql.connector
from config import mysql
from datetime import datetime, time, timedelta
import calendar
from MySQLdb.cursors import DictCursor


def get_connection():
    try:
        cursor = mysql.connection.cursor()
        return cursor
    except mysql.connector.Error as e:
        print("Database Connection Error:", e)
        return None

#login function

from werkzeug.security import check_password_hash

def check_login(username, password):

    conn = get_connection()

    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT *
            FROM employees
            WHERE (email = %s OR phone = %s)
            AND status = 'Active'
        """

        cursor.execute(query, (username, username))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            return user

        return None

    except Exception as e:
        print("Login Error:", e)
        return None

    finally:
        cursor.close()
        conn.close()

#get employee office location

def get_employee_location(emp_id):
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                l.location_id,
                l.location_name,
                l.city,
                l.latitude,
                l.longitude,
                l.radius
            FROM employees e
            JOIN locations l 
            ON e.location_id = l.location_id
            WHERE e.emp_id = %s
        """
        cursor.execute(query, (emp_id,))
        location = cursor.fetchone()
        return location

    except Exception as e:
        print("Location Error:", e)
        return None

    finally:
        cursor.close()
        conn.close()

#get deputed location

def get_deputed_location(emp_id):
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                deputed_id,
                emp_id,
                latitude,
                longitude,
                location_name,
                radius,
                from_date,
                to_date
            FROM employee_deputed_location
            WHERE emp_id = %s
            AND CURDATE() >= from_date
            AND (to_date IS NULL OR CURDATE() <= to_date)
            ORDER BY from_date DESC
            LIMIT 1
        """

        cursor.execute(query, (emp_id,))
        deputed = cursor.fetchone()

        print("ACTIVE DEPUTED FOUND:", deputed)

        return deputed

    except Exception as e:
        print("Deputed Location Error:", e)
        return None

    finally:
        cursor.close()
        conn.close()

#holiday check

def is_holiday(check_date):

    if check_date.weekday() == 6:
        return True

    if check_date.weekday() == 5:

        month_calendar = calendar.monthcalendar(
            check_date.year,
            check_date.month
        )

        saturday_count = 0

        for week in month_calendar:
            if week[calendar.SATURDAY] != 0:
                saturday_count += 1

                if week[calendar.SATURDAY] == check_date.day:
                    if saturday_count in [2, 4]:
                        return True

    return False

#day status

def calculate_day_status(work_hours):
    if work_hours >= 8:
        return "Full Day"
    elif work_hours > 0:
        return "Half Day"
    else:
        return "Absent"



# mark attendance

def mark_attendance(emp_id, lat, lon, inside_geofence, action):

    conn = get_connection()
    if not conn:
        return {"status": "error", "message": "Database connection failed"}

    cursor = conn.cursor(dictionary=True)

    today = datetime.now().date()
    now = datetime.now()

    try:
        if is_holiday(today):
            return {"status": "warning", "message": "Today is Holiday"}

        cursor.execute("""
            SELECT attendance_id, check_in, check_out
            FROM attendance_master
            WHERE emp_id = %s AND attendance_date = %s
        """, (emp_id, today))

        record = cursor.fetchone()

    
        # CHECK IN
        if action == "checkin":

            checkin_time = datetime.now().time()

            start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
            end_time = datetime.strptime("16:00:00", "%H:%M:%S").time()

            #  OUT OF TIME WINDOW
            if not (start_time <= checkin_time <= end_time):
                return {
                    "status": "error",
                    "message": "Check-in allowed only between 9 AM and 4 PM",
                    "current_time": str(checkin_time)
                }

            if record:
                return {"status": "warning", "message": "Already Checked In Today"}

            if not inside_geofence:
                return {"status": "error", "message": "Cannot Check In - Outside Office"}

            cursor.execute("""
                INSERT INTO attendance_master
                (
                    emp_id,
                    attendance_date,
                    check_in,
                    checkin_latitude,
                    checkin_longitude,
                    status
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                emp_id,
                today,
                now,
                lat,
                lon,
                "PRESENT"
            ))

            conn.commit()

            return {"status": "success", "message": "Checked In Successfully"}

        
        # CHECK OUT
        
        elif action == "checkout":

            if not record:
                return {"status": "warning", "message": "Please Check In First"}

            if record["check_out"] is not None:
                return {"status": "warning", "message": "Already Checked Out Today"}

            if not inside_geofence:
                return {"status": "error", "message": "Cannot Check Out - Outside Office"}

            work_seconds = (now - record["check_in"]).total_seconds()
            work_seconds = max(work_seconds, 0)

            work_hours = round(work_seconds / 3600, 2)

            if work_hours >= 8:
                final_status = "Full Day"
            elif work_hours > 0:
                final_status = "Half Day"
            else:
                final_status = "Absent"

            cursor.execute("""
                UPDATE attendance_master
                SET
                    check_out = %s,
                    checkout_latitude = %s,
                    checkout_longitude = %s,
                    work_hours = %s,
                    status = %s
                WHERE attendance_id = %s
            """, (
                now,
                lat,
                lon,
                work_hours,
                final_status,
                record["attendance_id"]
            ))

            conn.commit()

            return {
                "status": "success",
                "message": f"Checked Out - {final_status}"
            }

        else:
            return {"status": "error", "message": "Invalid Action"}

    except Exception as e:
        conn.rollback()
        print("Attendance Error:", e)
        return {"status": "error", "message": "Attendance Failed"}

    finally:
        cursor.close()
        conn.close()

# auto mark absent 

def auto_mark_absent():

    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)
    yesterday = datetime.now().date() - timedelta(days=1)

    try:

        if is_holiday(yesterday):
            return

        cursor.execute("SELECT emp_id FROM employees WHERE status='Active'")
        employees = cursor.fetchall()

        for emp in employees:

            cursor.execute("""
                SELECT attendance_id 
                FROM attendance_master
                WHERE emp_id=%s AND attendance_date=%s
            """, (emp["emp_id"], yesterday))

            record = cursor.fetchone()

            if not record:
                cursor.execute("""
                    INSERT INTO attendance_master
                    (emp_id, attendance_date, status)
                    VALUES (%s, %s, %s)
                """, (emp["emp_id"], yesterday, "Absent"))

        conn.commit()

    except Exception as e:
        print("Auto Absent Error:", e)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


# get attendance history

def get_attendance_history(emp_id):

    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                attendance_date,
                check_in,
                check_out,
                work_hours,
                status
            FROM attendance_master
            WHERE emp_id = %s
            ORDER BY attendance_date DESC
            LIMIT 30
        """, (emp_id,))

        history = cursor.fetchall()
        return history

    except Exception as e:
        print("History Error:", e)
        return []

    finally:
        cursor.close()
        conn.close()

# monthly report

def get_employee_monthly_report(emp_id, month, year):

    cursor = mysql.connection.cursor()
    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT 
            e.emp_id,
            e.full_name,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status,
            a.work_hours
        FROM attendance_master a
        JOIN employees e ON a.emp_id = e.emp_id
        WHERE a.emp_id = %s
        AND MONTH(a.attendance_date) = %s
        AND YEAR(a.attendance_date) = %s
    """, (emp_id, month, year))

    data = cursor.fetchall()
    cursor.close()

    return data

def get_admin_employee_report(emp_id, month, year):

    cursor = mysql.connection.cursor()
    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT 
            e.emp_id,
            e.full_name,

            COUNT(a.attendance_id) AS total_days,

            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present,

            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent,

            ROUND(SUM(IFNULL(a.work_hours, 0)), 2) AS total_work_hours,

            ROUND(
                (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0)
                / NULLIF(COUNT(a.attendance_id), 0), 2
            ) AS attendance_percentage

        FROM attendance_master a
        JOIN employees e ON a.emp_id = e.emp_id

        WHERE a.emp_id = %s
        AND MONTH(a.attendance_date) = %s
        AND YEAR(a.attendance_date) = %s

        GROUP BY a.emp_id, e.full_name
    """, (emp_id, month, year))

    data = cursor.fetchall()
    cursor.close()

    return data

def calculate_summary(report):

    if not report:
        return None

    r = report[0]   # only 1 employee record

    present = 0
    absent = 0
    total_hours = 0

    for row in report:

        if row["status"] in ["Present", "Full Day"]:
            present += 1
        else:
            absent += 1

        total_hours += row.get("work_hours") or 0

    total_days = present + absent

    attendance_percentage = round(
        (present / total_days) * 100, 2
    ) if total_days > 0 else 0

    return {
        "emp_id": r["emp_id"],
        "full_name": r["full_name"],
        "present": present,
        "absent": absent,
        "total_work_hours": round(total_hours, 2),
        "attendance_percentage": attendance_percentage
    }
    
# dashboard summary

def get_dashboard_summary(emp_id):

    conn = get_connection()
    if not conn:
        return {}

    cursor = conn.cursor(dictionary=True)

    today = datetime.now()
    first_day = today.replace(day=1).date()

    try:
        cursor.execute("""
            SELECT status, COUNT(*) as total
            FROM attendance_master
            WHERE emp_id=%s
            AND attendance_date >= %s
            GROUP BY status
        """, (emp_id, first_day))

        results = cursor.fetchall()

        summary = {
            "Full Day": 0,
            "Half Day": 0,
            "Absent": 0,
            "Holiday": 0,
            "Outside Geofence": 0
        }

        for row in results:
            status = row["status"]

            if status in ["Present", "Present (Late)"]:
                summary["Full Day"] += row["total"]

            elif status in summary:
                summary[status] = row["total"]


        return summary

    except Exception as e:
        print("Dashboard Error:", e)
        return {}

    finally:
        cursor.close()
        conn.close()