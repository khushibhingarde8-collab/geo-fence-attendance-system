from flask import Blueprint, request, jsonify, render_template, session, redirect
from config import mysql
from datetime import datetime
from MySQLdb.cursors import DictCursor
from flask_mail import Message
from app import mail
from flask import current_app

leave_bp = Blueprint("leave_bp", __name__)

# =========================================================
# LEAVE PAGE
# =========================================================

@leave_bp.route("/leave")
def leave_page():

    if "email" not in session:
        return redirect("/login")

    return render_template("leave_management.html")


# =========================================================
# USER PROFILE
# =========================================================

@leave_bp.route("/api/user/profile")
def user_profile():

    if "email" not in session:
        return jsonify({"error": "Login required"}), 401

    email = session["email"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT employee_id,
               CONCAT(first_name,' ',last_name) AS full_name,
               comp_mail,
               gender
        FROM employees
        WHERE (email=%s OR comp_mail=%s)
        AND is_active=TRUE
    """, (email, email))

    user = cur.fetchone()

    cur.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)


# =========================================================
# DASHBOARD
# =========================================================

@leave_bp.route("/api/leave/dashboard")
def dashboard():

    if "email" not in session:
        return jsonify({"available": 0, "pending": 0, "approved": 0})

    email = session["email"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT employee_id FROM employees
        WHERE email=%s OR comp_mail=%s
    """, (email, email))

    row = cur.fetchone()
    employee_id = row["employee_id"]

    cur.execute("""
        SELECT COUNT(*) AS approved
        FROM tbl_leaves
        WHERE employee_id=%s AND status='Approved'
    """, (employee_id,))
    approved = cur.fetchone()["approved"]

    cur.execute("""
        SELECT COUNT(*) AS pending
        FROM tbl_leaves
        WHERE employee_id=%s AND status='Pending'
    """, (employee_id,))
    pending = cur.fetchone()["pending"]

    available = 12 - approved

    cur.close()

    return jsonify({
        "available": available,
        "pending": pending,
        "approved": approved
    })

# =========================================================
# APPLY LEAVE
# =========================================================

@leave_bp.route("/api/leave/apply", methods=["POST"])
def apply_leave():

    if "email" not in session:
        return jsonify({"error": "Login required"}), 401

    email = session["email"]

    data = request.get_json()

    start_date = data.get("from_date")
    end_date = data.get("to_date")
    reason = data.get("reason")
    leave_type = data.get("leave_type")

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT
            employee_id,
            CONCAT(first_name,' ',last_name) AS employee_name,
            reporting_manager_id
        FROM employees
        WHERE email=%s OR comp_mail=%s
    """, (email, email))

    emp = cur.fetchone()

    employee_id = emp["employee_id"]
    employee_name = emp["employee_name"]
    manager_id = emp["reporting_manager_id"]

    cur.execute("""
        SELECT comp_mail
        FROM employees
        WHERE employee_id=%s
    """, (manager_id,))

    manager = cur.fetchone()

    manager_email = manager["comp_mail"] if manager else None

    cur.execute("""
        SELECT email
        FROM tbl_user
    """)

    admins = cur.fetchall()

    admin_emails = [row["email"] for row in admins]

    all_recipients = admin_emails.copy()

    if manager_email:
        all_recipients.append(manager_email)

    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    employee_id = emp["employee_id"]

    print("FORM DATA:", request.form)
    print("JSON DATA:", request.get_json(silent=True))

    print("start_date =", start_date)
    print("end_date =", end_date)


    if not start_date or not end_date:
        return jsonify({
            "error": "Start date and End date are required"
        }), 400

    sd = datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.strptime(end_date, "%Y-%m-%d")

    if ed < sd:
        return jsonify({"error": "Invalid dates"}), 400

    total_days = (ed - sd).days + 1

    # overlap check
    cur.execute("""
        SELECT leave_id
        FROM tbl_leaves
        WHERE employee_id=%s
        AND status IN ('Pending','Approved')
        AND NOT (end_date < %s OR start_date > %s)
    """, (employee_id, start_date, end_date))

    if cur.fetchone():
        return jsonify({"error": "Already applied"}), 400

    # insert
    cur.execute("""
        INSERT INTO tbl_leaves
        (employee_id, leave_type, start_date, end_date, total_days, reason, status)
        VALUES (%s,%s,%s,%s,%s,%s,'Pending')
    """, (employee_id, leave_type, start_date, end_date, total_days, reason))

    mysql.connection.commit()

    # Get reporting manager email
    cur.execute("""
        SELECT
            CONCAT(first_name,' ',last_name) AS manager_name,
            comp_mail
        FROM employees
        WHERE employee_id=%s
    """, (manager_id,))

    manager = cur.fetchone()

    if manager and manager["comp_mail"]:

        # msg = Message(
        #     subject="New Leave Request",
        #     sender="yourcompany@gmail.com",
        #     recipients=[manager["comp_mail"]]
        # )

        cur.execute("""
            SELECT email
            FROM tbl_user u
            JOIN tbl_user_role ur
            ON u.user_id = ur.user_id
            WHERE ur.role_id = 1
        """)

        admins = cur.fetchall()

        admin_emails = [row["email"] for row in admins]

        all_recipients = [manager_email] + admin_emails

        msg = Message(
            subject="New Leave Request",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=all_recipients
        )

        msg.body = f"""
    Hello {manager['manager_name']},

    A new leave request has been submitted.

    Employee: {employee_name}
    Leave Type: {leave_type}
    From: {start_date}
    To: {end_date}
    Reason: {reason}

    Please login to approve or reject the request.

    Regards,
    PCE Leave Management System
    """

    print("Manager Email:", manager_email)
    print("Admin Emails:", admin_emails)
    print("Recipients:", all_recipients)
    print("MAIL_USERNAME:", current_app.config.get("MAIL_USERNAME"))

    mail.send(msg)


    cur.close()

    return jsonify({"message": "Leave Applied Successfully"})

# =========================================================
# MY REQUESTS
# =========================================================

@leave_bp.route("/api/leave/my_requests")
def my_requests():

    if "employee_id" not in session:
        return jsonify([])

    employee_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT
            leave_id,
            start_date,
            end_date,
            reason,
            status,
            leave_type,
            total_days
        FROM tbl_leaves
        WHERE employee_id=%s
        ORDER BY leave_id DESC
    """, (employee_id,))

    data = cur.fetchall()

    cur.close()

    return jsonify(data)


# =========================================================
# LEAVE HISTORY
# =========================================================

@leave_bp.route("/api/leave/history")
def leave_history():

    if "employee_id" not in session:
        return jsonify([])

    employee_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT
            leave_id,
            start_date,
            end_date,
            reason,
            status,
            leave_type,
            total_days
        FROM tbl_leaves
        WHERE employee_id=%s
        ORDER BY leave_id DESC
    """, (employee_id,))

    data = cur.fetchall()

    cur.close()

    return jsonify(data)


# =========================================================
# CANCEL LEAVE
# =========================================================

@leave_bp.route("/api/leave/cancel/<int:leave_id>", methods=["POST"])
def cancel_leave(leave_id):

    if "employee_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    employee_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        UPDATE tbl_leaves
        SET status='Cancelled'
        WHERE leave_id=%s
        AND employee_id=%s
        AND status='Pending'
    """, (leave_id, employee_id))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Leave Cancelled Successfully"
    })


# =========================================================
# MANAGER TEAM LEAVES
# =========================================================

@leave_bp.route("/api/leave/team")
def team_leaves():

    if "employee_id" not in session:
        return jsonify([])

    manager_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT
            l.leave_id,
            CONCAT(e.first_name,' ',e.last_name) AS employee_name,
            l.start_date,
            l.end_date,
            l.reason,
            l.status,
            l.leave_type,
            l.total_days
        FROM tbl_leaves l

        JOIN employees e
        ON l.employee_id = e.employee_id

        WHERE e.reporting_manager_id=%s
        AND l.status='Pending'

        ORDER BY l.leave_id DESC
    """, (manager_id,))

    data = cur.fetchall()

    cur.close()

    return jsonify(data)


# =========================================================
# APPROVE LEAVE
# =========================================================

@leave_bp.route("/api/leave/approve/<int:leave_id>", methods=["POST"])
def approve_leave(leave_id):

    if "employee_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    manager_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        UPDATE tbl_leaves l

        JOIN employees e
        ON l.employee_id = e.employee_id

        SET l.status='Approved'

        WHERE l.leave_id=%s
        AND e.reporting_manager_id=%s
    """, (leave_id, manager_id))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Leave Approved Successfully"
    })


# =========================================================
# REJECT LEAVE
# =========================================================

@leave_bp.route("/api/leave/reject/<int:leave_id>", methods=["POST"])
def reject_leave(leave_id):

    if "employee_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    manager_id = session["employee_id"]

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        UPDATE tbl_leaves l

        JOIN employees e
        ON l.employee_id = e.employee_id

        SET l.status='Rejected'

        WHERE l.leave_id=%s
        AND e.reporting_manager_id=%s
    """, (leave_id, manager_id))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Leave Rejected Successfully"
    })