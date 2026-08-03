from flask import Blueprint, render_template, request, redirect, flash, session
from config import mysql
from datetime import datetime
import re

project_bp = Blueprint("project_bp", __name__)

# =========================
# PROJECT PAGE
# =========================
@project_bp.route("/project")
def project():
    return render_template("project/project.html")


# =========================
# PROJECT DETAIL PAGE
# =========================
@project_bp.route("/project-detail")
def project_detail():
    return render_template("project/projectDetail.html")

@project_bp.route("/project-list")
def project_list():
    return render_template("project/projectList.html")

@project_bp.route("/save_project", methods=["POST"])
def save_project():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    project_id = request.form.get("project_id")
    project_name = request.form.get("project_name")
    client_id = request.form.get("client_id")

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    project_status = request.form.get("project_status")



    # =========================
    # ✅ PROJECT NAME VALIDATION
    # =========================

    if len(project_name) > 100:

        flash("❌ Project Name too long", "project_msg")
        return redirect("/admin#projects")


    # repeated character validation
    if project_name.lower() == project_name[0].lower() * len(project_name):

        flash("❌ Invalid Project Name", "project_msg")
        return redirect("/admin#projects")



    # =========================
    # ✅ PROJECT NAME FORMAT
    # =========================

    if not re.match(r'^[A-Za-z0-9 ._-]+$', project_name):

        flash("❌ Invalid Project Name Format", "project_msg")
        return redirect("/admin#projects")



    # =========================
    # ✅ DATE VALIDATION
    # =========================

    try:

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        # end date before start date
        if end_date_obj < start_date_obj:

            flash("❌ End date cannot be before start date", "project_msg")
            return redirect("/admin#projects")

    except:

        flash("❌ Invalid date format", "project_msg")
        return redirect("/admin#projects")



    # =========================
    # DB STARTS AFTER VALIDATION
    # =========================

    cursor = mysql.connection.cursor()



    # =========================
    # 🔎 CHECK CLIENT EXISTS
    # =========================

    cursor.execute(
        "SELECT client_id FROM tbl_client WHERE client_id=%s",
        (client_id,)
    )

    client_exists = cursor.fetchone()

    if not client_exists:

        flash("❌ Client ID does not exist!", "project_msg")

        cursor.close()

        return redirect("/admin#projects")



    # =========================
    # 🔎 DUPLICATE PROJECT CHECK
    # =========================

    if action == "INSERT":

        cursor.execute(
            "SELECT * FROM tbl_project WHERE project_name=%s",
            (project_name,)
        )

        if cursor.fetchone():

            flash("❌ Project Name already exists!", "project_msg")

            cursor.close()

            return redirect("/admin#projects")



    elif action == "UPDATE":

        cursor.execute(
            """
            SELECT * FROM tbl_project
            WHERE project_name=%s
            AND project_id!=%s
            """,
            (project_name, project_id)
        )

        if cursor.fetchone():

            flash("❌ Project Name already exists!", "project_msg")

            cursor.close()

            return redirect("/admin#projects")



    # =========================
    # ✅ INSERT
    # =========================

    if action == "INSERT":

        cursor.execute("""

            INSERT INTO tbl_project
            (
                project_name,
                client_id,
                start_date,
                end_date,
                project_status
            )

            VALUES (%s, %s, %s, %s, %s)

        """, (

            project_name,
            client_id,
            start_date,
            end_date,
            project_status

        ))

        flash("✅ Project Added Successfully!", "project_msg")



    # =========================
    # ✅ UPDATE
    # =========================

    elif action == "UPDATE":

        cursor.execute("""

            UPDATE tbl_project

            SET
                project_name=%s,
                client_id=%s,
                start_date=%s,
                end_date=%s,
                project_status=%s

            WHERE project_id=%s

        """, (

            project_name,
            client_id,
            start_date,
            end_date,
            project_status,
            project_id

        ))

        flash("✅ Project Updated Successfully!", "project_msg")



    # =========================
    # ✅ DELETE
    # =========================

    elif action == "DELETE":

        cursor.execute("""

            UPDATE tbl_project

            SET is_active = FALSE

            WHERE project_id=%s

        """, (project_id,))

        flash("✅ Project Deleted Successfully!", "project_msg")



    mysql.connection.commit()

    cursor.close()

    return redirect("/admin#projects")
