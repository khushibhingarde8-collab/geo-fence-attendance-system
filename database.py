from datetime import datetime, time, timedelta
import calendar
from config import mysql   # or wherever you defined it


#login function

from werkzeug.security import check_password_hash
def check_login(username, password):

    conn = mysql.connection
    if not conn:
        return None

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    try:
        query = """
            SELECT *
            FROM tbl_user
            WHERE email = %s
            AND is_active = TRUE
        """

        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            return user

        return None

    except Exception as e:
        print("Login Error:", e)
        return None

    finally:
        cursor.close()

#get employee office location
def get_employee_location(employee_id):

    conn = mysql.connection
    if not conn:
        return None

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    try:
        query = """
            SELECT 
                location_id,
                location_name,
                city,
                latitude,
                longitude,
                radius
            FROM tbl_location
            WHERE location_id = (
                SELECT location_id 
                FROM employees 
                WHERE employee_id = %s
            )
        """

        cursor.execute(query, (employee_id,))
        return cursor.fetchone()

    except Exception as e:
        print("Location Error:", e)
        return None

    finally:
        cursor.close()
        

#get deputed location

def get_deputed_location(employee_id):

    conn = mysql.connection
    if not conn:
        return None

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    try:
        query = """
            SELECT 
                deputed_id,
                employee_id,
                latitude,
                longitude,
                location_name,
                radius,
                from_date,
                to_date
            FROM employee_deputed_location
            WHERE employee_id = %s
            AND CURDATE() >= from_date
            AND (to_date IS NULL OR CURDATE() <= to_date)
            ORDER BY from_date DESC
            LIMIT 1
        """

        cursor.execute(query, (employee_id,))
        return cursor.fetchone()

    except Exception as e:
        print("Deputed Location Error:", e)
        return None

    finally:
        cursor.close()
        

#holiday check

def is_holiday(check_date):

    conn = mysql.connection

    if not conn:
        return False

    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)
    
    try:
        cursor.execute("""
            SELECT 1
            FROM holiday_master
            WHERE holiday_date = %s
            LIMIT 1
        """, (check_date,))

        result = cursor.fetchone()

        print("HOLIDAY CHECK:", check_date, "RESULT:", result)

        return result is not None

    except Exception as e:
        print("Holiday Error:", e)
        return False

    finally:
        cursor.close()
        
        
import calendar

def is_weekly_off(check_date):
     #Sunday
    if check_date.weekday() == 6:
        return True

    # Saturday
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

#leave 
def is_on_approved_leave(employee_id, check_date):

    conn = mysql.connection

    from MySQLdb.cursors import DictCursor
    cursor = conn.cursor(DictCursor)

    try:

        cursor.execute("""
            SELECT 1
            FROM tbl_leaves
            WHERE employee_id = %s
            AND status = 'Approved'
            AND %s BETWEEN start_date AND end_date
            LIMIT 1
        """, (
            employee_id,
            check_date
        ))

        return cursor.fetchone() is not None

    finally:
        cursor.close()

#day status

def calculate_day_status(work_hours):

    if work_hours >= 8:
        return "Present"

    elif work_hours >= 4:
        return "Half Day"

    else:
        return "Absent"

# mark attendance
def mark_attendance(employee_id, lat, lon, inside_geofence, action):

    print(">>>>>>>> INSIDE THIS mark_attendance() <<<<<<<<")
    conn = mysql.connection
    if not conn:
        return {"status": "error", "message": "Database connection failed"}

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    today = datetime.now().date()
    now = datetime.now()

    try:
        # if is_weekly_off(today):
        #     return {
        #         "status": "warning",
        #         "message": "Today is Weekly Off"
        #     }

        if is_holiday(today):
            return {
                "status": "warning",
                "message": "Today is Holiday"
            }

        # if is_on_approved_leave(employee_id, today):
        #     return {
        #         "status": "warning",
        #         "message": "You are on Approved Leave"
        #     }   

        cursor.execute("""
            SELECT attendance_id, check_in, check_out
            FROM attendance_master
            WHERE employee_id = %s AND attendance_date = %s
        """, (employee_id, today))

        record = cursor.fetchone()

    
        # CHECK IN
        if action == "checkin":

            checkin_time = datetime.now().time()
            arrival_status = "On Time"

            if checkin_time > datetime.strptime("10:00:00", "%H:%M:%S").time():
                arrival_status = "Late"

            start_time = datetime.strptime("9:00:00", "%H:%M:%S").time()
            end_time = datetime.strptime("23:00:00", "%H:%M:%S").time()

            #  OUT OF TIME WINDOW
            if not (start_time <= checkin_time <= end_time):
                return {
                    "status": "error",
                    "message": "Check-in allowed only between 9 AM and 7 PM",
                    "current_time": str(checkin_time)
                }

            if record and record["check_in"] is not None:
                return {
                    "status": "warning",
                    "message": "Already Checked In Today"
                }

            if not inside_geofence:
                return {"status": "error", "message": "Cannot Check In - Outside Office"}

            cursor.execute("""
                INSERT INTO attendance_master
                (
                    employee_id,
                    attendance_date,
                    check_in,
                    checkin_latitude,
                    checkin_longitude,
                    status,
                    arrival_status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                employee_id,
                today,
                now,
                lat,
                lon,
                "Present",
                arrival_status
            ))

            conn.commit()

            # ==========================================
            # RESET TRACKING FOR NEW CHECK-IN
            # ==========================================
            cursor.execute("""
                UPDATE tracking
                SET
                    outside_count = 0,
                    warning_sent = 0,
                    outside_since = NULL,
                    location_status = 'Inside'
                WHERE employee_id = %s
            """, (employee_id,))

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

            check_in = record["check_in"]   # ✅ FIXED INDENTATION

            # safe conversion
            if isinstance(check_in, str):
                check_in = datetime.strptime(check_in, "%Y-%m-%d %H:%M:%S")

            work_seconds = (now - check_in).total_seconds()
            work_seconds = max(work_seconds, 0)

            work_hours = round(work_seconds / 3600, 2)

            final_status = calculate_day_status(work_hours)

            # =====================================
            # OVERTIME CALCULATION
            # Office timing ends at 7:00 PM
            # =====================================

            office_end = datetime.combine(today, time(19, 0))

            if now > office_end:
                overtime_minutes = int(
                    (now - office_end).total_seconds() // 60
                )
            else:
                overtime_minutes = 0

            cursor.execute("""
                UPDATE attendance_master
                SET
                    check_out = %s,
                    checkout_latitude = %s,
                    checkout_longitude = %s,
                    work_hours = %s,
                    overtime_minutes = %s,
                    status = %s,
                    checkout_type = %s
                WHERE attendance_id = %s
            """, (
                now,
                lat,
                lon,
                work_hours,
                overtime_minutes,
                final_status,
                "manual",
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
        import traceback
        traceback.print_exc()
        conn.rollback()

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        cursor.close()

def attendance_engine():

     conn = mysql.connection
     cursor = conn.cursor()

     today = datetime.now().date()

     # Stop on holiday or weekly off
     if is_holiday(today) or is_weekly_off(today):
         cursor.close()
         return

     # Insert Absent for employees who have no attendance record today
     cursor.execute("""
         INSERT INTO attendance_master (employee_id, attendance_date, status)
         SELECT e.employee_id, %s, 'Absent'
         FROM employees e
         WHERE e.is_active = 1
         AND e.employee_id NOT IN (
             SELECT employee_id
             FROM attendance_master
             WHERE attendance_date = %s
         )
     """, (today, today))

     conn.commit()
     cursor.close()

def auto_force_checkout():

    conn = mysql.connection

    if not conn:
        return

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    today = datetime.now().date()
    now = datetime.now()

    try:

        # Find employees who checked in but forgot to check out
        cursor.execute("""
            SELECT
                attendance_id,
                employee_id,
                check_in
            FROM attendance_master
            WHERE attendance_date = %s
            AND check_in IS NOT NULL
            AND check_out IS NULL
        """, (today,))

        records = cursor.fetchall()

        for record in records:

            check_in = record["check_in"]

            # Safe conversion
            if isinstance(check_in, str):
                check_in = datetime.strptime(
                    check_in,
                    "%Y-%m-%d %H:%M:%S"
                )

            # Calculate work hours
            work_seconds = (now - check_in).total_seconds()
            work_seconds = max(work_seconds, 0)

            work_hours = round(work_seconds / 3600, 2)

            # Calculate final attendance status
            final_status = calculate_day_status(work_hours)

            # Overtime starts after 7:00 PM
            office_end = datetime.combine(today, time(19, 0))

            if now > office_end:
                overtime_minutes = int(
                    (now - office_end).total_seconds() // 60
                )
            else:
                overtime_minutes = 0

            # Update attendance
            cursor.execute("""
                UPDATE attendance_master
                SET
                    check_out = %s,
                    work_hours = %s,
                    overtime_minutes = %s,
                    status = %s,
                    checkout_type = %s
                WHERE attendance_id = %s
            """, (
                now,
                work_hours,
                overtime_minutes,
                final_status,
                "Auto Force Checkout",
                record["attendance_id"]
            ))

        conn.commit()

        print(f"Auto Force Checkout Completed. Processed {len(records)} employees.")

    except Exception as e:
        conn.rollback()
        print("Auto Force Checkout Error:", e)

    finally:
        cursor.close()

# get attendance history

def get_attendance_history(employee_id):

    conn = mysql.connection
    if not conn:
        return []

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    try:
        cursor.execute("""
            SELECT
                attendance_date,
                check_in,
                check_out,
                work_hours,
                status,
                arrival_status,
                overtime_minutes,
                checkout_type
            FROM attendance_master
            WHERE employee_id=%s
            ORDER BY attendance_date DESC
            LIMIT 30
        """, (employee_id,))

        history = cursor.fetchall()
        return history

    except Exception as e:
        print("History Error:", e)
        return []

    finally:
        cursor.close()

# monthly report

def get_employee_monthly_report(employee_id, month, year):

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT 
            e.employee_id,
            CONCAT(e.first_name,' ',e.last_name) AS full_name,
            a.attendance_date,
            a.check_in,
            a.check_out,
            a.status,
            a.work_hours
        FROM attendance_master a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE a.employee_id = %s
        AND MONTH(a.attendance_date) = %s
        AND YEAR(a.attendance_date) = %s
    """, (employee_id, month, year))

    data = cursor.fetchall()

    return data

def get_admin_employee_report(employee_id, month, year):

    conn = mysql.connection
    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT 
            e.employee_id,
            CONCAT(e.first_name,' ',e.last_name) AS full_name,

            COUNT(a.attendance_id) AS total_days,

            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present,

            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent,

            ROUND(SUM(IFNULL(a.work_hours, 0)), 2) AS total_work_hours,

            ROUND(
                (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0)
                / NULLIF(COUNT(a.attendance_id), 0), 2
            ) AS attendance_percentage

        FROM attendance_master a
        JOIN employees e ON a.employee_id = e.employee_id

        WHERE a.employee_id = %s
        AND MONTH(a.attendance_date) = %s
        AND YEAR(a.attendance_date) = %s

        GROUP BY
            a.employee_id,
            e.first_name,
            e.last_name
    """, (employee_id, month, year))

    data = cursor.fetchall()
    

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
        "employee_id": r["employee_id"],
        "full_name": r["full_name"],
        "present": present,
        "absent": absent,
        "total_work_hours": round(total_hours, 2),
        "attendance_percentage": attendance_percentage
    }
    
# dashboard summary

def get_dashboard_summary(employee_id):

    conn = mysql.connection
    if not conn:
        return {}

    from MySQLdb.cursors import DictCursor

    cursor = conn.cursor(DictCursor)

    today = datetime.now()
    first_day = today.replace(day=1).date()

    try:
        cursor.execute("""
            SELECT status, COUNT(*) as total
            FROM attendance_master
            WHERE employee_id=%s
            AND attendance_date >= %s
            GROUP BY status
        """, (employee_id, first_day))

        results = cursor.fetchall()

        summary = {
            "Present": 0,
            "Late": 0,
            "Full Day": 0,
            "Half Day": 0,
            "Absent": 0,
            "Holiday": 0,
            "Leave": 0
        }

        for row in results:
            status = row["status"]

            if status in summary:
                summary[status] = row["total"]

        return summary

    except Exception as e:
        print("Dashboard Error:", e)
        return {}

    finally:
        cursor.close()
        