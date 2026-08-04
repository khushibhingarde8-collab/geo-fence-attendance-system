from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from config import mysql
from MySQLdb.cursors import DictCursor

admin_mobile_bp = Blueprint("admin_mobile_bp", __name__)


# ======================================
# ADMIN MOBILE LOGIN
# ======================================
@admin_mobile_bp.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No data received"
        }), 400

    email = data.get("email")
    password = data.get("password")
    fcm_token = data.get("fcm_token")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    try:

        cursor.execute("""
            SELECT
            u.user_id,
            u.email,
            u.password_hash,
            u.is_active,
            r.role_name
        FROM tbl_user u
        JOIN tbl_user_role ur
            ON u.user_id = ur.user_id
        JOIN tbl_role r
            ON ur.role_id = r.role_id
        WHERE u.email = %s
            AND u.is_active = TRUE
            AND LOWER(r.role_name) = 'admin'
        LIMIT 1
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401
        
        # Save Admin FCM Token
        if fcm_token:
            cursor.execute("""
                UPDATE tbl_user
                SET fcm_token = %s
                WHERE user_id = %s
            """, (fcm_token, user["user_id"]))

            conn.commit()

        return jsonify({
        "status": "success",
        "message": "Login successful",
        "role": user["role_name"],
        "user_id": user["user_id"],
        "email": user["email"]
        }), 200
    except Exception as e:

        print("ADMIN LOGIN ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server Error"
        }), 500

    finally:
        if cursor:
            cursor.close()