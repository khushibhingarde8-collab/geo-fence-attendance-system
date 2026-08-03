from flask import Blueprint, request, redirect, flash, session
from config import mysql

location_bp = Blueprint("location_bp", __name__)


@location_bp.route("/save_location", methods=["POST"])
def save_location():

    # LOGIN CHECK
    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    location_id = request.form.get("location_id")
    location_name = request.form.get("location_name")

    cursor = mysql.connection.cursor()

    try:

        # ======================
        # INSERT
        # ======================

        if action == "INSERT":

            cursor.execute("""
                INSERT INTO locations
                (location_name)
                VALUES (%s)
            """, (location_name,))

            flash("✅ Location Added Successfully", "location_msg")

        # ======================
        # UPDATE
        # ======================

        elif action == "UPDATE":

            cursor.execute("""
                UPDATE locations
                SET location_name=%s
                WHERE location_id=%s
            """, (
                location_name,
                location_id
            ))

            flash("✅ Location Updated Successfully", "location_msg")

        # ======================
        # DELETE
        # ======================

        elif action == "DELETE":

            cursor.execute("""
                DELETE FROM locations
                WHERE location_id=%s
            """, (location_id,))

            flash("✅ Location Deleted Successfully", "location_msg")

        mysql.connection.commit()

    except Exception as e:

        mysql.connection.rollback()

        flash(f"❌ Error: {str(e)}", "location_msg")

    finally:
        cursor.close()

    return redirect("/admin#locations")