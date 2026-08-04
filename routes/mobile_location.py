from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from config import mysql
from MySQLdb.cursors import DictCursor
from utils import calculate_distance
import smtplib
from email.mime.text import MIMEText
from firebase_service import send_push_notification

mobile_location_bp = Blueprint("mobile_location_bp", __name__)


# =====================================================
# EMAIL FUNCTION
# =====================================================
def send_warning_email(to_email, employee_id):

    sender_email = "yourgmail@gmail.com"
    sender_password = "your_app_password"

    subject = "Warning - Geofence Violation"

    body = f"""
Employee {employee_id},

You have repeatedly moved outside the office geofence.

Please be careful.

HR System
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()


# =====================================================
# TRACK LOCATION
# =====================================================
@mobile_location_bp.route("/api/track_location", methods=["POST"])
def track_location():

    conn = None

    try:
        data = request.get_json()

        employee_id = data["employee_id"]
        lat = float(data["latitude"])
        lon = float(data["longitude"])

        conn = mysql.connection
        cursor = conn.cursor(DictCursor)

        now = datetime.now()

        # ---------------- EMP EMAIL ----------------
        cursor.execute("""
            SELECT CONCAT(first_name, ' ', last_name) AS full_name, email
            FROM employees
            WHERE employee_id=%s
            """, (employee_id,))

        emp = cursor.fetchone()

        if not emp:
            return jsonify({"error": "Employee not found"})

        employee_name = emp["full_name"]
        email = emp["email"]

        # ---------------- OFFICE ----------------
        # ---------------- OFFICE ----------------
        cursor.execute("""
            SELECT
                l.latitude,
                l.longitude,
                l.radius
            FROM employees e
            JOIN tbl_location l 
            ON e.location_id = l.location_id
            WHERE e.employee_id = %s
        """, (employee_id,))

        office = cursor.fetchone()

        if not office:
            return jsonify({"error": "Office not found"})

        office_lat = float(office["latitude"])
        office_lon = float(office["longitude"])
        radius = float(office["radius"])

        # ---------------- DISTANCE ----------------
        distance = calculate_distance(lat, lon, office_lat, office_lon)
        inside = distance <= radius
        current_status = "Inside" if inside else "Outside"

        # ---------------- PREVIOUS STATUS ----------------
        cursor.execute("""
            SELECT location_status
            FROM tracking
            WHERE employee_id=%s
        """, (employee_id,))

        old = cursor.fetchone()

        previous_status = None

        if old:
            previous_status = old["location_status"]

        

        # ---------------- STATUS CHANGE NOTIFICATION ----------------
        if previous_status and previous_status != current_status:

            cursor.execute("""
                INSERT INTO notifications
                (
                    employee_id,
                    message,
                    notification_type
                )
                VALUES(%s,%s,%s)
                """, (
                employee_id,
                f"{employee_name} moved {previous_status} → {current_status}",
                "admin"
                ))

            conn.commit()
        # ---------------- CHECK-IN ----------------
        cursor.execute("""
            SELECT check_in, check_out
            FROM attendance_master
            WHERE employee_id=%s
            AND attendance_date=CURDATE()
        """, (employee_id,))

        att = cursor.fetchone()

        if not att or not att["check_in"]:
            return jsonify({"status": "no checkin"})
        
        # Employee already checked out → stop tracking
        if att["check_out"]:
            return jsonify({
                "status": "already_checked_out"
        })


        # ---------------- TRACK TABLE ----------------
        cursor.execute("""
            INSERT INTO tracking
                (
                employee_id,
                latitude,
                longitude,
                location_status,
                last_updated
                )
                VALUES(%s,%s,%s,%s,NOW())

                ON DUPLICATE KEY UPDATE
                latitude=%s,
                longitude=%s,
                location_status=%s,
                last_updated=NOW()
        """, (
            employee_id, lat, lon, "Inside" if inside else "Outside",
            lat, lon, "Inside" if inside else "Outside"
        ))

        conn.commit()

    

         #Reset outside count for a new day
        cursor.execute("""
             UPDATE tracking
             SET outside_count = 0,
                 warning_sent = 0,
                 outside_since = NULL
             WHERE employee_id = %s
             AND DATE(last_updated) < CURDATE()
         """, (employee_id,))

        conn.commit()

        # ---------------- TRACK DATA ----------------
        cursor.execute("""
            SELECT outside_count, warning_sent, outside_since
            FROM tracking
            WHERE employee_id=%s
        """, (employee_id,))

        t = cursor.fetchone()

        if not t:
            outside_count = 0
            warning_sent = 0
            outside_since = None
        else:
            outside_count = t["outside_count"] or 0
            warning_sent = t["warning_sent"] or 0
            outside_since = t["outside_since"]

        # =================================================
        # INSIDE CASE
        # =================================================
        if inside:

            cursor.execute("""
                UPDATE tracking
                SET
                    outside_since = NULL,
                    location_status = 'Inside',
                    last_updated=NOW()
                WHERE employee_id = %s
            """, (employee_id,))

            conn.commit()

        # =================================================
        # OUTSIDE CASE
        # =================================================
        else:

            # start timer
            if outside_since is None:
                cursor.execute("""
                    UPDATE tracking
                    SET outside_since=NOW()
                    WHERE employee_id=%s
                """, (employee_id,))
                conn.commit()

            else:

                diff = now - outside_since

                # only count if 5 min passed
                if diff >= timedelta(minutes=5):

                    outside_count += 1

                    cursor.execute("""
                        UPDATE tracking
                        SET outside_count=%s,
                            outside_since=NOW(),
                            last_updated=NOW()
                        WHERE employee_id=%s
                    """, (outside_count, employee_id))

                    conn.commit()

                    # ---------------- LEVEL 2 WARNING ----------------
                    if outside_count == 2 and warning_sent == 0:

                        cursor.execute("""
                            UPDATE tracking
                            SET warning_sent = 1
                            WHERE employee_id = %s
                        """, (employee_id,))

                        cursor.execute("""
                            INSERT INTO notifications(employee_id, message,notification_type)
                            VALUES(%s,%s,%s)
                        """, (
                            employee_id,
                            "⚠ You are outside the office geofence. Please return immediately.",
                              "employee"
                            ))

                        conn.commit()

                        # Get employee FCM token
                        cursor.execute("""
                            SELECT fcm_token ,CONCAT(first_name, ' ', last_name) AS full_name
                            FROM employees
                            WHERE employee_id=%s
                        """, (employee_id,))

                        employee = cursor.fetchone()

                        if employee and employee["fcm_token"]:

                            send_push_notification(
                            employee["fcm_token"],
                            "⚠ Geofence Warning",
                            "You are outside the office geofence. Please return immediately."
                            )

                        # ===========================
                        # Admin Website Notification
                        # ===========================
                        cursor.execute("""
                            INSERT INTO notifications(employee_id, message, notification_type)
                            VALUES(%s, %s, %s)
                        """, (
                            employee_id,
                            f"⚠ Warning: {employee['full_name']} has been outside the office geofence for a long time.",
                            "admin"
                            ))

                        conn.commit()

                        # -------------------------------
                        # Get all Admin FCM Tokens
                        # -------------------------------
                        cursor.execute("""
                            SELECT u.fcm_token
                            FROM tbl_user u
                            JOIN tbl_user_role ur ON u.user_id = ur.user_id
                            JOIN tbl_role r ON ur.role_id = r.role_id
                            WHERE r.role_name = 'admin'
                            AND u.fcm_token IS NOT NULL
                        """)

                        admins = cursor.fetchall()

                        # -------------------------------
                            # -------------------------------
                        for admin in admins:

                            send_push_notification(
                                admin["fcm_token"],
                                "🚨 Employee Outside Geofence",
                                f"{employee['full_name']} has been outside the office geofence for a long time."
                                )
                    # ---------------- FORCE CHECKOUT ----------------
                    # ---------------- FORCE CHECKOUT ----------------
                    if outside_count >= 3:

                        print("FORCE CHECKOUT BLOCK ENTERED")
                        print("Employee ID:", employee_id)
                        print("Outside Count:", outside_count)

                        cursor.execute("""
                            SELECT check_out
                            FROM attendance_master
                            WHERE employee_id=%s
                            AND attendance_date=CURDATE()
                        """, (employee_id,))

                        chk = cursor.fetchone()

                        print("Attendance Record:", chk)

                        if not chk or not chk["check_out"]:

                            print("CHECKOUT IS NULL, UPDATING...")

                            cursor.execute("""
                            UPDATE attendance_master
                            SET
                                check_out=NOW(),
                                checkout_type='Force Checkout'
                            WHERE employee_id=%s
                            AND attendance_date=CURDATE()
                            AND check_out IS NULL
                            """, (employee_id,))

                            print("Rows Updated:", cursor.rowcount)

                            conn.commit()

                            print("FORCE CHECKOUT COMMITTED")

                            cursor.execute("""
                                UPDATE tracking
                                SET
                                    location_status='Checked Out',
                                    outside_since=NULL,
                                    warning_sent=0
                                WHERE employee_id=%s
                                """, (employee_id,))

                            conn.commit()


                            # ==========================
                            # STEP 3: EMPLOYEE NOTIFICATION (DB)
                            # ==========================
                            cursor.execute("""
                                INSERT INTO notifications(employee_id, message, notification_type)
                                VALUES(%s, %s, %s)
                            """, (
                                employee_id,
                                "⚠ You have been automatically checked out due to long absence outside the office.",
                                "employee"
                                 ))


                            conn.commit()
                            # reset tracking so it doesn't re-trigger
                            cursor.execute("""
                                UPDATE tracking
                                SET outside_since=NULL
                                WHERE employee_id=%s
                            """, (employee_id,))
                            conn.commit()

                            # compute work hours safely
                            cursor.execute("""
                                SELECT check_in, check_out
                                FROM attendance_master
                                WHERE employee_id=%s AND attendance_date=CURDATE()
                            """, (employee_id,))

                            a = cursor.fetchone()

                            if a and a["check_in"] and a["check_out"]:

                                work_hours = (
                                (a["check_out"] - a["check_in"]).total_seconds() / 3600
                                )

                                work_hours = round(work_hours, 2)

                                if work_hours >= 8:
                                    status = "Present"
                                elif work_hours >= 4:
                                    status = "Half Day"
                                else:
                                    status = "Absent"

                                cursor.execute("""
                                    UPDATE attendance_master
                                    SET
                                        work_hours=%s,
                                        status=%s
                                    WHERE employee_id=%s
                                    AND attendance_date=CURDATE()
                                    """, (
                                    work_hours,
                                    status,
                                    employee_id
                                    ))

                                conn.commit()
                            cursor.execute("""
                                INSERT INTO notifications
                                (
                                    employee_id,
                                    message,
                                    notification_type
                                )
                                VALUES(%s,%s,%s)
                                """, (
                                    employee_id,
                                    "AUTO FORCE CHECKOUT DONE",
                                    "admin"
                                ))

                            conn.commit()

                            # ==========================================
                            # SEND FORCE CHECKOUT POPUP TO ALL ADMINS
                            # ==========================================

                            # Get employee name
                            cursor.execute("""
                                SELECT CONCAT(first_name, ' ', last_name) AS full_name
                                FROM employees
                                WHERE employee_id=%s
                            """, (employee_id,))

                            employee = cursor.fetchone()

                            # Get all Admin FCM tokens
                            cursor.execute("""
                                SELECT u.fcm_token
                                FROM tbl_user u
                                JOIN tbl_user_role ur
                                    ON u.user_id = ur.user_id
                                JOIN tbl_role r
                                    ON ur.role_id = r.role_id
                                WHERE r.role_name='admin'
                                AND u.fcm_token IS NOT NULL
                            """)

                            admins = cursor.fetchall()

                            # Send popup to every admin
                            for admin in admins:

                                send_push_notification(
                                    admin["fcm_token"],
                                    "🚨 Force Checkout",
                                f"{employee['full_name']} has been automatically force checked out."
                            )

                            cursor.execute("""
                                SELECT fcm_token
                                FROM employees
                                WHERE employee_id=%s
                            """, (employee_id,))

                            employee = cursor.fetchone()

                            if employee and employee["fcm_token"]:

                                send_push_notification(
                                    employee["fcm_token"],
                                    "Automatic Checkout",
                                    "You have been automatically checked out because you stayed outside the office geofence."
                                )
                            
                            return jsonify({
                                "status": "force_checkout"
                                })

        return jsonify({
            "status": "success",
            "inside": inside,
            "outside_count": outside_count
        })

    except Exception as e:

        print("ERROR OCCURRED:", e)

        if conn:
            conn.rollback()

        return jsonify({"error": str(e)})

    finally:
        if conn:
            cursor.close()

@mobile_location_bp.route('/api/employee_notifications/<int:employee_id>')
def employee_notifications(employee_id):

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            notification_id,
            message,
            created_at
        FROM notifications
        WHERE employee_id=%s
        AND notification_type='employee'
        ORDER BY notification_id DESC
    """, (employee_id,))

    rows = cursor.fetchall()

    cursor.close()

    return jsonify(rows)


@mobile_location_bp.route("/api/admin_notifications")
def admin_notifications():

    cursor = mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT
            notification_id,
            employee_id,
            message,
            created_at
        FROM notifications
        WHERE notification_type='admin'
        ORDER BY notification_id DESC
    """)

    rows = cursor.fetchall()

    cursor.close()

    return jsonify(rows)