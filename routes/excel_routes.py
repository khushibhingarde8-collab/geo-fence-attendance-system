
import io
import pandas as pd
from flask import Blueprint, session, redirect, send_file, flash
from config import mysql
from datetime import datetime
from openpyxl.styles import Font

excel_bp = Blueprint("excel_bp", __name__)




def export_query_to_excel(query, sheet_name, filename_prefix):

    df = pd.read_sql(query, con=mysql.connection)

    # Automatically format all datetime/date columns
    for column in df.columns:
        try:
            converted = pd.to_datetime(df[column], errors="raise")
            df[column] = converted.dt.strftime("%d-%m-%Y")
        except:
            pass

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        ws = writer.sheets[sheet_name]

        # Make header bold
        for cell in ws[1]:
            cell.font = Font(bold=True)

        # Auto-adjust column widths
        for column_cells in ws.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                try:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            ws.column_dimensions[column_letter].width = max_length + 3

    output.seek(0)

    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# client
@excel_bp.route("/export/clients")
def export_clients():

    if "user_id" not in session:
        return redirect("/login")

    query = """
    SELECT
        client_id AS 'Client ID',
        client_name AS 'Client Name',
        client_code AS 'Client Code',
        email,
        phone,
        city,
        state,
        country,
        gst_number,
        pan_number
    FROM tbl_client
    """

    return export_query_to_excel(query, "Clients", "Clients")


# Project
@excel_bp.route("/export/projects")
def export_projects():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT

            p.project_id AS 'Project ID',
            p.project_name AS 'Project Name',

            c.client_name AS 'Client Name',

            p.start_date AS 'Start Date',
            p.end_date AS 'End Date',

            p.project_status AS 'Status'

        FROM tbl_project p

        LEFT JOIN tbl_client c
        ON p.client_id = c.client_id

        ORDER BY p.project_name
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Projects")

        output.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return send_file(
            output,
            as_attachment=True,
            download_name=f"Projects_{timestamp}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(f"Error exporting projects: {e}", "error")
        return redirect("/admin#projects")

# employee
@excel_bp.route("/export/employees")
def export_employees():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """

        SELECT

            e.employee_id AS 'Employee ID',
            e.employee_code AS 'Employee Code',

            e.first_name AS 'First Name',
            e.last_name AS 'Last Name',

            e.dob AS 'Date Of Birth',
            e.doj AS 'Date Of Joining',

            p.project_name AS 'Project',

            e.phone AS 'Phone',
            e.aadhar_number AS 'Aadhar Number',
            e.pan_number AS 'PAN Number',

            e.email AS 'Personal Email',
            e.comp_mail AS 'Company Email',

            e.gender AS 'Gender',

            d.department_name AS 'Department',

            des.designation_name AS 'Designation',

            CONCAT(rm.first_name,' ',rm.last_name)
            AS 'Reporting Manager',

            l.location_name AS 'Location',

            g.grade_name AS 'Grade'

        FROM employees e

        LEFT JOIN tbl_project p
        ON e.project_id = p.project_id

        LEFT JOIN tbl_department d
        ON e.department_id = d.department_id

        LEFT JOIN tbl_designation des
        ON e.designation_id = des.designation_id

        LEFT JOIN employees rm
        ON e.reporting_manager_id = rm.employee_id

        LEFT JOIN tbl_location l
        ON e.location_id = l.location_id

        LEFT JOIN tbl_grade g
        ON e.grade_id = g.grade_id

        ORDER BY e.employee_code

        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Employees")

        output.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return send_file(
            output,
            as_attachment=True,
            download_name=f"Employees_{timestamp}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(f"Error exporting employees: {e}", "error")
        return redirect("/admin#employees")

# department
@excel_bp.route("/export/departments")
def export_departments():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT
            department_id AS 'Department ID',
            department_name AS 'Department Name'
        FROM tbl_department
        ORDER BY department_name
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Departments")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Departments.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e), "error")
        return redirect("/admin#department-designation")

# designation
@excel_bp.route("/export/designations")
def export_designations():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT
            designation_id AS 'Designation ID',
            designation_name AS 'Designation Name'
        FROM tbl_designation
        ORDER BY designation_name
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Designations")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Designations.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#department-designation")

# location 
@excel_bp.route("/export/locations")
def export_locations():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT

        location_id AS 'Location ID',
        location_name AS 'Location Name',
        country AS Country,
        state AS State,
        city AS City,
        latitude AS Latitude,
        longitude AS Longitude,
        radius AS Radius

        FROM tbl_location

        ORDER BY location_name
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Locations")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Locations.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#location-grade")


# grade
@excel_bp.route("/export/grades")
def export_grades():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT

        grade_id AS 'Grade ID',
        grade_name AS 'Grade Name',
        grade_level AS 'Grade Level'

        FROM tbl_grade

        ORDER BY grade_level
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Grades")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Grades.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#location-grade")


# 
@excel_bp.route("/export/employee-logins")
def export_employee_logins():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query = """
        SELECT

            login_id AS 'Login ID',
            email AS 'Email',

            CASE
                WHEN is_active=1 THEN 'Active'
                ELSE 'Inactive'
            END AS Status

        FROM tbl_login

        WHERE role_id=2

        ORDER BY login_id DESC
        """

        df = pd.read_sql(query, con=mysql.connection)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Employee Logins")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Employee_Logins.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#emplogin")


# login
@excel_bp.route("/export/admin-logins")
def export_admin_logins():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query="""

        SELECT

        login_id AS 'Login ID',
        email AS Email,

        CASE
            WHEN is_active=1 THEN 'Active'
            ELSE 'Inactive'
        END AS Status

        FROM tbl_login

        WHERE role_id=1

        ORDER BY login_id DESC

        """

        df=pd.read_sql(query,con=mysql.connection)

        output=io.BytesIO()

        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Admin Logins")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Admin_Logins.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#emplogin")


# leave
@excel_bp.route("/export/leaves")
def export_leaves():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query="""

        SELECT

        l.leave_id AS 'Leave ID',

        CONCAT(e.first_name,' ',e.last_name)
        AS Employee,

        l.from_date AS 'From Date',

        l.to_date AS 'To Date',

        l.reason AS Reason,

        l.status AS Status

        FROM leave_requests l

        JOIN employees e
        ON l.emp_id=e.employee_id

        ORDER BY l.leave_id DESC

        """

        df=pd.read_sql(query,con=mysql.connection)

        output=io.BytesIO()

        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Leaves")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="Leave_Report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#leaves")


# tds
@excel_bp.route("/export/tds")
def export_tds():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query="""

        SELECT

        id AS 'Upload ID',

        original_file_name AS 'File Name',

        uploaded_at AS 'Uploaded On'

        FROM tbl_tds_uploads

        ORDER BY uploaded_at DESC

        """

        df=pd.read_sql(query,con=mysql.connection)

        output=io.BytesIO()

        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="TDS Uploads")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="TDS_Uploads.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#tdscert")


# news
@excel_bp.route("/export/news")
def export_news():

    if "user_id" not in session:
        return redirect("/login")

    try:

        query="""

        SELECT

        news_id AS 'News ID',

        title AS Title,

        description AS Description,

        news_date AS Date,

        external_link AS 'External Link'

        FROM tbl_news

        ORDER BY news_date DESC

        """

        df=pd.read_sql(query,con=mysql.connection)

        output=io.BytesIO()

        with pd.ExcelWriter(output,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="News")

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="News.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        flash(str(e),"error")
        return redirect("/admin#news")


@excel_bp.route("/export/home-purpose")
def export_home_purpose():

    if "user_id" not in session:
        return redirect("/login")

    query="""

    SELECT

    id,
    title,
    description

    FROM tbl_home_purpose

    """

    df=pd.read_sql(query,con=mysql.connection)

    output=io.BytesIO()

    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        df.to_excel(writer,index=False,sheet_name="Purpose")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Purpose.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# journy
@excel_bp.route("/export/journey")
def export_journey():

    if "user_id" not in session:
        return redirect("/login")

    query="""

    SELECT

    journey_id,
    year,
    title,
    description

    FROM tbl_home_journey

    ORDER BY year

    """

    df=pd.read_sql(query,con=mysql.connection)

    output=io.BytesIO()

    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        df.to_excel(writer,index=False,sheet_name="Journey")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Journey.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# business
@excel_bp.route("/export/business-scope")
def export_business_scope():

    if "user_id" not in session:
        return redirect("/login")

    query="""

    SELECT

    scope_id,
    title,
    description

    FROM tbl_home_business_scope

    """

    df=pd.read_sql(query,con=mysql.connection)

    output=io.BytesIO()

    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        df.to_excel(writer,index=False,sheet_name="Business Scope")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Business_Scope.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# home certificate
@excel_bp.route("/export/home-certificates")
def export_home_certificates():

    if "user_id" not in session:
        return redirect("/login")

    query="""

    SELECT

    certificate_id,

    title,

    description,

    image_path,

    pdf_path

    FROM tbl_home_certificate

    """

    df=pd.read_sql(query,con=mysql.connection)

    output=io.BytesIO()

    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        df.to_excel(writer,index=False,sheet_name="Certificates")

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Certificates.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )




