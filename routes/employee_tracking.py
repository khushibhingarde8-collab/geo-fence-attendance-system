from flask import Blueprint, render_template, jsonify
from config import mysql
from MySQLdb.cursors import DictCursor
employee_tracking_bp = Blueprint("employee_tracking_bp", __name__)


# =====================================================
# DASHBOARD
# =====================================================
@employee_tracking_bp.route('/employee_tracking')
def employee_tracking():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,

            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            a.checkout_type,

            CASE
                WHEN a.check_out IS NOT NULL THEN 'Checked Out'
                ELSE t.location_status
            END AS location_status,

            t.last_updated,
            t.outside_count,
            t.warning_sent

        FROM employees e

        INNER JOIN attendance_master a
            ON e.employee_id = a.employee_id
            AND a.attendance_date = CURDATE()
            AND a.check_in IS NOT NULL

        LEFT JOIN tracking t
            ON e.employee_id = t.employee_id

        ORDER BY e.employee_id
    """)

    rows = cursor.fetchall()
    cursor.close()

    return render_template(
        "employee_tracking.html",
        data=rows
    )


# =====================================================
# LIVE API
# =====================================================
@employee_tracking_bp.route('/api/tracking_data')
def tracking_data():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,

            a.check_in,
            a.check_out,
            a.status AS attendance_status,
            a.checkout_type,

            CASE
                WHEN a.check_out IS NOT NULL THEN 'Checked Out'
                ELSE t.location_status
            END AS location_status,
            t.last_updated,
            t.outside_count,
            t.warning_sent

        FROM employees e

        INNER JOIN attendance_master a
            ON e.employee_id = a.employee_id
            AND a.attendance_date = CURDATE()
            AND a.check_in IS NOT NULL

        LEFT JOIN tracking t
            ON e.employee_id = t.employee_id

        ORDER BY e.employee_id
    """)

    rows = cursor.fetchall()
    cursor.close()

    return jsonify(rows)


# =====================================================
# NOTIFICATIONS
# =====================================================
@employee_tracking_bp.route('/api/notifications')
def notifications():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            n.notification_id,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,
            n.message,
            n.created_at
        FROM notifications n
        JOIN employees e
            ON n.employee_id = e.employee_id
        WHERE DATE(n.created_at) = CURDATE()
        AND n.notification_type = 'admin'
        ORDER BY n.notification_id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    cursor.close()

    return jsonify(row if row else {})


# =====================================================
# ALL NOTIFICATIONS
# =====================================================
@employee_tracking_bp.route('/api/all_notifications')
def all_notifications():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            n.notification_id,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,
            n.message,
            n.created_at,
            n.is_read
        FROM notifications n
        JOIN employees e
            ON n.employee_id = e.employee_id
        WHERE DATE(n.created_at) = CURDATE()
        AND n.notification_type = 'admin'  
        ORDER BY n.created_at DESC
    """)

    rows = cursor.fetchall()
    cursor.close()

    return jsonify(rows)

# =====================================================
# EMPLOYEE NOTIFICATIONS
# =====================================================
@employee_tracking_bp.route('/api/employee_notifications/<int:employee_id>')
def employee_notifications(employee_id):

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            notification_id,
            message,
            created_at
        FROM notifications
        WHERE employee_id = %s
        AND notification_type = 'employee'
        ORDER BY notification_id DESC
    """, (employee_id,))

    rows = cursor.fetchall()

    cursor.close()

    return jsonify(rows)


# =====================================================
# CLEAR NOTIFICATIONS
# =====================================================
@employee_tracking_bp.route(
    '/api/clear_notifications',
    methods=['POST']
)
def clear_notifications():

    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM notifications
        WHERE DATE(created_at) = CURDATE()
    """)

    conn.commit()
    cursor.close()

    return jsonify({
        "status": "success"
    })


@employee_tracking_bp.route('/api/admin_dashboard')
def admin_dashboard():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    # ===========================
    # TOTAL EMPLOYEES
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM employees
    """)
    employees = cursor.fetchone()["total"]

    # ===========================
    # PRESENT
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM attendance_master
        WHERE attendance_date = CURDATE()
        AND status = 'Present'
    """)
    present = cursor.fetchone()["total"]

    # ===========================
    # HALF DAY (optional)
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM attendance_master
        WHERE attendance_date = CURDATE()
        AND status = 'Half Day'
    """)
    half_day = cursor.fetchone()["total"]

    # ===========================
    # ABSENT
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM attendance_master
        WHERE attendance_date = CURDATE()
        AND status = 'Absent'
    """)
    absent = cursor.fetchone()["total"]

    # ===========================
    # INSIDE OFFICE
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tracking t
        JOIN attendance_master a
            ON t.employee_id = a.employee_id
        WHERE a.attendance_date = CURDATE()
        AND a.check_in IS NOT NULL
        AND a.check_out IS NULL
        AND t.location_status = 'Inside'
    """)
    inside = cursor.fetchone()["total"]

    # ===========================
    # OUTSIDE OFFICE
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tracking t
        JOIN attendance_master a
            ON t.employee_id = a.employee_id
        WHERE a.attendance_date = CURDATE()
        AND a.check_in IS NOT NULL
        AND a.check_out IS NULL
        AND t.location_status = 'Outside'
    """)
    outside = cursor.fetchone()["total"]

    # ===========================
    # FORCE CHECKOUT
    # ===========================
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM attendance_master
        WHERE attendance_date = CURDATE()
        AND checkout_type = 'Force Checkout'
    """)
    force_out = cursor.fetchone()["total"]

    # ===========================
    # TOTAL OUTSIDE COUNT
    # ===========================
    cursor.execute("""
        SELECT IFNULL(SUM(outside_count),0) AS total
        FROM tracking
    """)
    outside_count = cursor.fetchone()["total"]

    cursor.close()

    return jsonify({
        "employees": employees,
        "present": present,
        "half_day": half_day,
        "absent": absent,
        "inside": inside,
        "outside": outside,
        "force_out": force_out,
        "outside_count": outside_count
    })


# =====================================================
# EMPLOYEES BY STATUS
# =====================================================
@employee_tracking_bp.route('/api/admin/employees/<status>')
def employees_by_status(status):

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    if status == "inside":

        cursor.execute("""
            SELECT
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) AS full_name,
                t.location_status,
                a.check_in
            FROM employees e
            JOIN tracking t
                ON e.employee_id = t.employee_id
            JOIN attendance_master a
                ON e.employee_id = a.employee_id
            WHERE a.attendance_date = CURDATE()
            AND a.check_in IS NOT NULL
            AND a.check_out IS NULL
            AND t.location_status = 'Inside'
            ORDER BY  e.employee_id
        """)

    elif status == "outside":

        cursor.execute("""
            SELECT
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) AS full_name,
                t.location_status,
                t.outside_count,
                a.check_in
            FROM employees e
            JOIN tracking t
                ON e.employee_id = t.employee_id
            JOIN attendance_master a
                ON e.employee_id = a.employee_id
            WHERE a.attendance_date = CURDATE()
            AND a.check_in IS NOT NULL
            AND a.check_out IS NULL
            AND t.location_status = 'Outside'
            ORDER BY  e.employee_id
        """)

    elif status == "present":

        cursor.execute("""
            SELECT
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) AS full_name,
                a.check_in,
                a.check_out,
                a.work_hours,
                a.overtime_minutes,
                a.status,
                a.arrival_status,
                a.checkout_type
            FROM employees e
            JOIN attendance_master a
                ON e.employee_id = a.employee_id
            WHERE a.attendance_date = CURDATE()
            AND a.status IN ('Present', 'Late', 'Half Day','Full Day')
            ORDER BY e.employee_id
        """)

    elif status == "absent":

        cursor.execute("""
            SELECT
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) AS full_name,
                a.status
            FROM employees e
            JOIN attendance_master a
                ON e.employee_id = a.employee_id
            WHERE a.attendance_date = CURDATE()
            AND a.status = 'Absent'
            ORDER BY CONCAT(e.first_name,' ',e.last_name)
        """)

    elif status == "force_out":

        cursor.execute("""
            SELECT
                e.employee_id,
                CONCAT(e.first_name, ' ', e.last_name) AS full_name,
                a.check_in,
                a.check_out,
                a.checkout_type
            FROM employees e
            JOIN attendance_master a
                ON e.employee_id = a.employee_id
            WHERE a.attendance_date = CURDATE()
            AND a.checkout_type = 'Force Checkout'
            ORDER BY CONCAT(e.first_name,' ',e.last_name)
        """)

    else:
        cursor.close()
        return jsonify([])

    rows = cursor.fetchall()
    cursor.close()

    return jsonify(rows)

# =====================================================
# ALL EMPLOYEES
# =====================================================
@employee_tracking_bp.route('/api/employees')
def all_employees():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT
            e.employee_id,
            e.employee_code,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,
            e.email,
            l.location_name

        FROM employees e

        LEFT JOIN tbl_location l
            ON e.location_id = l.location_id

        ORDER BY e.employee_id
    """)

    rows = cursor.fetchall()

    cursor.close()
    

    return jsonify(rows)

    # =====================================================
# LIVE MAP API
# =====================================================
@employee_tracking_bp.route('/api/admin/live_map')
def admin_live_map():

    conn = mysql.connection
    cursor = conn.cursor(DictCursor)

    cursor.execute("""
        SELECT

            e.employee_id,
            CONCAT(e.first_name, ' ', e.last_name) AS full_name,

            t.latitude,
            t.longitude,
            t.location_status,
            t.last_updated,

            l.location_name,
            l.city,
            l.latitude AS office_lat,
            l.longitude AS office_lon,
            l.radius

        FROM employees e

        JOIN tracking t
            ON e.employee_id = t.employee_id

        JOIN tbl_location l
            ON e.location_id = l.location_id

        JOIN attendance_master a
            ON e.employee_id = a.employee_id

        WHERE a.attendance_date = CURDATE()
        AND a.check_in IS NOT NULL
        AND a.check_out IS NULL

        ORDER BY CONCAT(e.first_name,' ',e.last_name)

    """)

    rows = cursor.fetchall()

    cursor.close()

    return jsonify(rows)