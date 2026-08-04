from flask import Blueprint, jsonify
from config import mysql

report_bp = Blueprint("report_bp", __name__)


@report_bp.route('/api/report/<int:employee_id>/<int:month>/<int:year>', methods=['GET'])
def report(employee_id, month, year):

    conn = mysql.connection
    cursor = conn.cursor(dictionary=True)

    try:
        # ================= PRESENT =================
        cursor.execute("""
            SELECT COUNT(*) AS present
            FROM attendance_master
            WHERE employee_id=%s
            AND MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND status IN ('Present','Full Day')
        """, (employee_id, month, year))

        present = cursor.fetchone()["present"]

        # ================= ABSENT =================
        cursor.execute("""
            SELECT COUNT(*) AS absent
            FROM attendance_master
            WHERE employee_id=%s
            AND MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
            AND status='Absent'
        """, (employee_id, month, year))

        absent = cursor.fetchone()["absent"]

        # ================= WORK HOURS =================
        cursor.execute("""
            SELECT COALESCE(SUM(work_hours),0) AS total_hours
            FROM attendance_master
            WHERE employee_id=%s
            AND MONTH(attendance_date)=%s
            AND YEAR(attendance_date)=%s
        """, (employee_id, month, year))

        total_hours = cursor.fetchone()["total_hours"]

        return jsonify({
            "employee_id": employee_id,
            "present": present,
            "absent": absent,
            "total_hours": float(total_hours)
        })

    finally:
        cursor.close()