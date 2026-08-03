from flask import Blueprint, request, redirect, flash, session
from config import mysql

grade_bp = Blueprint("grade_bp", __name__)

@grade_bp.route("/save_grade", methods=["POST"])
def save_grade():
    # LOGIN CHECK
    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")
    grade_id = request.form.get("grade_id")
    grade_name = request.form.get("grade_name")
    grade_level = request.form.get("grade_level", 0)

    cursor = mysql.connection.cursor()

    try:
        # ======================
        # INSERT
        # ======================
        if action == "INSERT":
            cursor.execute("""
                INSERT INTO tbl_grade
                (grade_name, grade_level)
                VALUES (%s, %s)
            """, (grade_name, grade_level))
            flash("✅ Grade Added Successfully", "location_grade_msg")

        # ======================
        # UPDATE
        # ======================
        elif action == "UPDATE":
            cursor.execute("""
                UPDATE tbl_grade
                SET grade_name=%s, grade_level=%s
                WHERE grade_id=%s
            """, (grade_name, grade_level, grade_id))
            flash("✅ Grade Updated Successfully", "location_grade_msg")

        # ======================
        # DELETE
        # ======================
        elif action == "DELETE":
            cursor.execute("""
                DELETE FROM tbl_grade
                WHERE grade_id=%s
            """, (grade_id,))
            flash("✅ Grade Deleted Successfully", "location_grade_msg")

        mysql.connection.commit()

    except Exception as e:
        mysql.connection.rollback()
        flash(f"❌ Error: {str(e)}", "location_grade_msg")

    finally:
        cursor.close()

    return redirect("/admin#location-grade")
