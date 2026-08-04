from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from config import mysql
from MySQLdb.cursors import DictCursor
import random
from datetime import datetime, timedelta

from flask_mail import Message
from flask import current_app
from flask_mail import Message
from extensions import mail

# Blueprint
mobile_auth_bp = Blueprint(
    "mobile_auth",
    __name__
)


def send_reset_otp_email(email, otp):

    msg = Message(
        subject="Password Reset OTP",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body = f"""
Hello,

A password reset request was received for your GeoFence Attendance account.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
GeoFence Attendance System
"""

    mail.send(msg)

# =====================================================
# =====================================================
# SEND RESET OTP
# =====================================================
@mobile_auth_bp.route("/api/send_reset_otp", methods=["POST"])
def send_reset_otp():

    data = request.get_json()

    email = data.get("email", "").strip()

    if not email:
        return jsonify({
            "status": "error",
            "message": "Email is required"
        })

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:

        cursor.execute("""
            SELECT employee_id
            FROM app_users
            WHERE app_email=%s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "Email not registered"
            })

        employee_id = user["employee_id"]

        # Delete any previous OTP
        cursor.execute("""
            DELETE FROM password_reset_otp
            WHERE employee_id=%s
        """, (employee_id,))

        otp = str(random.randint(100000, 999999))

        expires = datetime.now() + timedelta(minutes=5)

        cursor.execute("""
            INSERT INTO password_reset_otp
            (
                employee_id,
                otp,
                expires_at
            )
            VALUES(%s,%s,%s)
        """, (
            employee_id,
            otp,
            expires
        ))

        conn.commit()

        send_reset_otp_email(email, otp)

        return jsonify({
            "status": "success",
            "message": "OTP sent successfully"
        })

    except Exception as e:

        print("SEND OTP ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server Error"
        })

    finally:
        cursor.close()


@mobile_auth_bp.route("/api/test_send_reset_otp")
def test_send_reset_otp():

    send_reset_otp_email(
        "khushibhingarde8@gmail.com",   # Replace with your email
        "123456"
    )

    return "OTP Email Sent"

# =====================================================
# VERIFY RESET OTP
# =====================================================
@mobile_auth_bp.route("/api/verify_reset_otp", methods=["POST"])
def verify_reset_otp():

    data = request.get_json()

    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({
            "status": "error",
            "message": "Email and OTP are required"
        })

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:

        cursor.execute("""
            SELECT employee_id
            FROM app_users
            WHERE app_email=%s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            })

        employee_id = user["employee_id"]

        cursor.execute("""
            SELECT *
            FROM password_reset_otp
            WHERE employee_id=%s
            ORDER BY id DESC
            LIMIT 1
        """, (employee_id,))

        record = cursor.fetchone()

        if not record:
            return jsonify({
                "status": "error",
                "message": "OTP not found"
            })

        if datetime.now() > record["expires_at"]:
            return jsonify({
                "status": "error",
                "message": "OTP expired"
            })

        if otp != record["otp"]:
            return jsonify({
                "status": "error",
                "message": "Invalid OTP"
            })

        cursor.execute("""
            UPDATE password_reset_otp
            SET verified=1
            WHERE id=%s
        """, (record["id"],))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "OTP verified"
        })

    except Exception as e:

        print("VERIFY OTP ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server Error"
        })

    finally:
        cursor.close()


@mobile_auth_bp.route("/api/reset_password", methods=["POST"])
def reset_password():

    data = request.get_json()

    email = data.get("email")
    new_password = data.get("new_password")

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:

        cursor.execute("""
            SELECT employee_id
            FROM app_users
            WHERE app_email=%s
        """,(email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status":"error",
                "message":"User not found"
            })


        hashed = generate_password_hash(
            new_password
        )


        cursor.execute("""
            UPDATE app_users
            SET app_password=%s,
            is_first_login=FALSE
            WHERE employee_id=%s
        """,
        (
            hashed,
            user["employee_id"]
        ))


        conn.commit()


        return jsonify({
            "status":"success",
            "message":"Password changed successfully"
        })


    except Exception as e:

        print(e)

        return jsonify({
            "status":"error",
            "message":"Server error"
        })


    finally:
        cursor.close()                    
# =====================================================
# LOGIN
# =====================================================
@mobile_auth_bp.route("/api/login", methods=["POST"])
def api_login():

    print("\n========== LOGIN API HIT ==========")

    data = request.get_json()
    print("STEP 1 - Data Received:", data)

    if not data:
        print("STEP 2 - No data received")
        return jsonify({
            "status": "error",
            "message": "No data received"
        })

    email = data.get("email")
    password = data.get("password")
    fcm_token = data.get("fcm_token")

    print("STEP 3 - Email:", email)

    if not email or not password:
        print("STEP 4 - Missing email/password")
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        })

    print("STEP 5 - Getting MySQL connection...")
    conn = mysql.connection
    print("STEP 6 - Connection:", conn)

    cursor = conn.cursor(DictCursor)
    print("STEP 7 - Cursor created")

    try:

        print("STEP 8 - Executing SQL...")

        cursor.execute("""
            SELECT
                au.employee_id,
                au.app_email,
                au.app_password,
                au.is_first_login,
                e.first_name,
                e.last_name,
                e.is_active
            FROM app_users au
            JOIN employees e
                ON au.employee_id = e.employee_id
            WHERE au.app_email = %s
            AND e.is_active = TRUE
        """, (email,))

        print("STEP 9 - SQL Executed")

        user = cursor.fetchone()

        print("STEP 10 - User Found:", user)

        if user:

            print("STEP 11 - Checking Password")

            ok = check_password_hash(
                user["app_password"],
                password
            )

            print("STEP 12 - Password Match:", ok)

            if ok:

                print("STEP 13 - Login Success")

                # Save Employee FCM Token
                if fcm_token:
                    cursor.execute("""
                        UPDATE employees
                        SET fcm_token = %s
                        WHERE employee_id = %s
                    """, (
                        fcm_token,
                        user["employee_id"]
                    ))

                    conn.commit()

                return jsonify({
                    "status": "success",
                    "employee_id": user["employee_id"],
                    "employee_name":
                        f"{user['first_name']} {user['last_name']}",
                    "first_login": user["is_first_login"]
                })

        print("STEP 14 - Invalid Credentials")

        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        })

    except Exception as e:

        print("STEP 15 - LOGIN ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server error"
        })

    finally:
        print("STEP 16 - Cursor Closed")
        cursor.close()

# =====================================================
# FORGOT PASSWORD
# =====================================================
@mobile_auth_bp.route("/api/forgot_password", methods=["POST"])
def api_forgot_password():

    data = request.get_json()

    email = data.get("email")
    dob = data.get("dob")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not email:
        return jsonify({
            "status": "error",
            "message": "Email required"
        })

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:
        cursor.execute("""
            SELECT
                au.employee_id,
                e.dob
            FROM app_users au
            JOIN employees e
                ON au.employee_id = e.employee_id
            WHERE au.app_email = %s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            })

        db_dob = str(user["dob"])

        if db_dob != dob:
            return jsonify({
                "status": "error",
                "message": "Wrong DOB"
            })

        if new_password != confirm_password:
            return jsonify({
                "status": "error",
                "message": "Passwords do not match"
            })

        hashed_password = generate_password_hash(
            new_password
        )

        cursor.execute("""
            UPDATE app_users
            SET app_password=%s,
                is_first_login=FALSE
            WHERE employee_id=%s
        """, (
            hashed_password,
            user["employee_id"]
        ))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Password reset successful"
        })

    except Exception as e:
        print("FORGOT PASSWORD ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server error"
        })

    finally:
        cursor.close()


# =====================================================
# CHANGE PASSWORD
# =====================================================
@mobile_auth_bp.route("/api/change_password", methods=["POST"])
def change_password():

    data = request.get_json()

    employee_id = data.get("employee_id")
    new_password = data.get("new_password")

    if not employee_id or not new_password:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        })

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:

        hashed_password = generate_password_hash(
            new_password
        )

        cursor.execute("""
            UPDATE app_users
            SET app_password=%s,
                is_first_login=FALSE
            WHERE employee_id=%s
        """, (
            hashed_password,
            employee_id
        ))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Password updated"
        })

    except Exception as e:
        print("CHANGE PASSWORD ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Update failed"
        })

    finally:
        cursor.close()