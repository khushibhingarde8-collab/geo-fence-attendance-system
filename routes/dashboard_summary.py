from flask import Blueprint, jsonify
from utils import calculate_distance
from datetime import datetime
from config import mysql

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/api/dashboard_summary/<int:employee_id>")
def dashboard_summary(employee_id):


    try:
        conn = mysql.connection
        
        from MySQLdb.cursors import DictCursor

        cursor = conn.cursor(DictCursor)

        now = datetime.now()
        year = now.year
        month = now.month

        # =============================
        # EMPLOYEE INFO
        # =============================
        cursor.execute("""
            SELECT
                employee_id,
                CONCAT(first_name,' ',last_name) AS full_name,
                location_id
            FROM employees
            WHERE employee_id=%s
        """, (employee_id,))
        emp = cursor.fetchone()

        if not emp:
            return jsonify({"error": "Employee not found"}), 404

        # =============================
        # OFFICE LOCATION
        # =============================
        cursor.execute("""
            SELECT latitude, longitude, radius
            FROM employee_deputed_location
            WHERE employee_id = %s
            AND from_date <= CURDATE()
            AND (to_date IS NULL OR to_date >= CURDATE())
            ORDER BY from_date DESC
            LIMIT 1
        """, (employee_id,))
        deputed = cursor.fetchone()

        if deputed:
            office_lat = float(deputed["latitude"] or 0)
            office_lon = float(deputed["longitude"] or 0)
            radius = float(deputed["radius"] or 0)
            office_type = "deputed"

        else:
            cursor.execute("""
                SELECT latitude, longitude, radius
                FROM tbl_location
                WHERE location_id=%s
            """, (emp["location_id"],))
            office = cursor.fetchone()

            if not office:
                return jsonify({"error": "Office location not found"}), 404

            office_lat = float(office["latitude"] or 0)
            office_lon = float(office["longitude"] or 0)
            radius = float(office["radius"] or 0)
            office_type = "default"

        # =============================
        # PRESENT (MONTHLY)
        # =============================
        cursor.execute("""
            SELECT COUNT(*) as present
            FROM attendance_master
            WHERE employee_id = %s
            AND status IN ('Present','Late','Full Day')
            AND MONTH(attendance_date) = %s
            AND YEAR(attendance_date) = %s
        """, (employee_id, month, year))
        present = cursor.fetchone()["present"]

        # =============================
        # ABSENT (MONTHLY)
        # =============================
        cursor.execute("""
            SELECT COUNT(*) as absent
            FROM attendance_master
            WHERE employee_id = %s
            AND status = 'Absent'
            AND MONTH(attendance_date) = %s
            AND YEAR(attendance_date) = %s
        """, (employee_id, month, year))
        absent = cursor.fetchone()["absent"]

        # =============================
        # HALF DAY (MONTHLY)
        # =============================
        cursor.execute("""
            SELECT COUNT(*) as half_day
            FROM attendance_master
            WHERE employee_id = %s
            AND status = 'Half Day'
            AND MONTH(attendance_date) = %s
            AND YEAR(attendance_date) = %s
        """, (employee_id, month, year))
        half_day = cursor.fetchone()["half_day"]

        # =============================
        # LATE (MONTHLY)
        # =============================
        cursor.execute("""
            SELECT COUNT(*) AS late_count
            FROM attendance_master
            WHERE employee_id = %s
            AND arrival_status = 'Late'
            AND MONTH(attendance_date) = %s
            AND YEAR(attendance_date) = %s
        """, (employee_id, month, year))
        late_count = cursor.fetchone()["late_count"]

        # =============================
        # LEAVE (FROM tbl_leaves)
        # =============================
        cursor.execute("""
            SELECT COALESCE(SUM(
                DATEDIFF(
                    LEAST(end_date, LAST_DAY(DATE(CONCAT(%s,'-',%s,'-01')))),
                    GREATEST(start_date, DATE(CONCAT(%s,'-',%s,'-01')))
                ) + 1
            ), 0) AS leave_count
            FROM tbl_leaves
            WHERE employee_id = %s
            AND status = 'Approved'
            AND start_date <= LAST_DAY(DATE(CONCAT(%s,'-',%s,'-01')))
            AND end_date >= DATE(CONCAT(%s,'-',%s,'-01'))
        """, (year, month, year, month, employee_id, year, month, year, month))

        leave_count = cursor.fetchone()["leave_count"]
        # =============================
        # HOLIDAYS (MONTHLY)
        # =============================
        cursor.execute("""
            SELECT COUNT(*) as holidays
            FROM holiday_master
            WHERE MONTH(holiday_date) = %s
            AND YEAR(holiday_date) = %s
        """, (month, year))

        holidays = cursor.fetchone()["holidays"]

        # =============================
        # LAST GPS
        # =============================
        cursor.execute("""
            SELECT latitude, longitude, last_updated,location_status,outside_count
            FROM tracking
            WHERE employee_id=%s
            ORDER BY last_updated DESC
            LIMIT 1
        """, (employee_id,))
        gps = cursor.fetchone()

        distance = 0
        inside = False
        gps_lat = 0.0
        gps_lon = 0.0

        if gps and gps["latitude"] is not None and gps["longitude"] is not None:
            gps_lat = float(gps["latitude"])
            gps_lon = float(gps["longitude"])

            distance = calculate_distance(
                gps_lat,
                gps_lon,
                office_lat,
                office_lon
            )

            inside = distance <= radius

            print("===== DASHBOARD =====")
            print("GPS:", gps_lat, gps_lon)
            print("OFFICE:", office_lat, office_lon)
            print("RADIUS:", radius)
            print("DISTANCE:", distance)
            print("INSIDE:", inside)
            print("=====================")

        cursor.close()
        

        # =============================
        # RESPONSE
        # =============================
        return jsonify({
            "employee_id": emp["employee_id"],
            "employee_name": emp["full_name"],

            "present": present,
            "absent": absent,
            "half_day": half_day,
            "late": late_count,
            "leave": leave_count,
            "holidays": holidays,

            "office_lat": office_lat,
            "office_lon": office_lon,
            "radius": radius,
            "office_type": office_type,

            "gps_lat": gps_lat,
            "gps_lon": gps_lon,

            "distance": round(distance, 2),
            "inside_geofence": inside,

            "last_updated": (
                str(gps["last_updated"]) 
                if gps and gps.get("last_updated") 
                else None
            ),  

            "location_status": gps["location_status"],
            "outside_count": gps["outside_count"]
              })

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500