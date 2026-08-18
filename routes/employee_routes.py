import re
from flask import Blueprint, request, redirect, flash, session, render_template, send_file
from config import mysql
from datetime import datetime
import os, json
from dateutil.relativedelta import relativedelta
from datetime import date
from werkzeug.utils import secure_filename
from flask import send_from_directory
from werkzeug.security import generate_password_hash

employee_bp = Blueprint("employee_bp", __name__)


@employee_bp.route("/save_employee", methods=["POST"])
def save_employee():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    employee_id = request.form.get("employee_id")
    employee_code = request.form.get("employee_code")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    dob = request.form.get("dob")
    doj = request.form.get("doj")

    project_id = request.form.get("project_id") or None

    phone = request.form.get("phone") or None
    aadhar_number = request.form.get("aadhar_number") or None
    pan_number = request.form.get("pan_number") or None

    email = request.form["email"]
    comp_mail = request.form["comp_mail"]
    

    gender = request.form.get("gender")
    department_id = request.form.get("department_id")
    designation_id = request.form.get("designation_id")
    reporting_manager_id = request.form.get("reporting_manager_id")

    location_id = request.form.get("location_id")
    grade_id = request.form.get("grade_id")


    reporting_manager_id = request.form.get("reporting_manager_id")

    if reporting_manager_id:
        reporting_manager_id = int(reporting_manager_id)
    else:
        reporting_manager_id = None

        

    # =========================
    # ✅ NAME VALIDATION
    # =========================

    if len(first_name) > 50:
        flash("❌ First Name too long", "employee_msg")
        return redirect("/admin#employees")

    if len(last_name) > 50:
        flash("❌ Last Name too long", "employee_msg")
        return redirect("/admin#employees")


    # repeated characters validation
    if first_name.lower() == first_name[0].lower() * len(first_name):
        flash("❌ Invalid First Name", "employee_msg")
        return redirect("/admin#employees")

    if last_name.lower() == last_name[0].lower() * len(last_name):
        flash("❌ Invalid Last Name", "employee_msg")
        return redirect("/admin#employees")


    # only alphabets validation
    if not re.match(r'^[A-Za-z ]+$', first_name):
        flash("❌ First Name should contain only alphabets", "employee_msg")
        return redirect("/admin#employees")

    if not re.match(r'^[A-Za-z ]+$', last_name):
        flash("❌ Last Name should contain only alphabets", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ EMPLOYEE CODE VALIDATION
    # =========================

    if len(employee_code) > 15:
        flash("❌ Employee Code too long", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ EMAIL VALIDATION
    # =========================

    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        flash("❌ Invalid Personal Email", "employee_msg")
        return redirect("/admin#employees")

    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', comp_mail):
        flash("❌ Invalid Company Email", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ PHONE VALIDATION
    # =========================

    if not re.match(r'^[0-9]{10}$', phone):
        flash("❌ Invalid Phone Number", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ PAN VALIDATION
    # =========================

    pan_number = pan_number.upper()

    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
        flash("❌ Invalid PAN Number", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ AADHAR VALIDATION
    # =========================

    if not re.match(r'^[0-9]{12}$', aadhar_number):
        flash("❌ Invalid Aadhaar Number", "employee_msg")
        return redirect("/admin#employees")



    # =========================
    # ✅ DATE VALIDATION
    # =========================

    try:

        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        doj_date = datetime.strptime(doj, "%Y-%m-%d")

        today = datetime.today()

        # future DOB check
        if dob_date > today:

            flash("❌ DOB cannot be in future", "employee_msg")
            return redirect("/admin#employees")


        # DOJ before DOB check
        if doj_date < dob_date:

            flash("❌ Joining Date cannot be before DOB", "employee_msg")
            return redirect("/admin#employees")

    except:

        flash("❌ Invalid Date Format", "employee_msg")
        return redirect("/admin#employees")



    cursor = mysql.connection.cursor()

    try:

        # =========================
        # INSERT
        # =========================

        if action == "INSERT":

            cursor.execute("""
                INSERT INTO employees
                (
                    employee_code,
                    first_name,
                    last_name,
                    dob,
                    doj,
                    project_id,
                    phone,
                    aadhar_number,
                    pan_number,
                    email,
                    comp_mail,
                    gender,
                    department_id,
                    designation_id,
                    reporting_manager_id,
                    location_id,
                    grade_id
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (

                employee_code,
                first_name,
                last_name,
                dob,
                doj,
                project_id,
                phone,
                aadhar_number,
                pan_number,
                email,
                comp_mail,
                gender,
                department_id,
                designation_id,
                reporting_manager_id,
                location_id,
                grade_id
            ))

            # Get the newly inserted employee ID
            employee_id = cursor.lastrowid

            print("New Employee ID:", employee_id)

            # Create leave balance
            cursor.execute("""
                INSERT INTO leave_balance
                (
                    employee_id,
                    total_leaves,
                    used_leaves
                )
                VALUES (%s, 1.5, 0)
            """, (employee_id,))

            

            flash("✅ Employee Added Successfully!", "employee_msg")




        # =========================
        # UPDATE
        # =========================

        elif action == "UPDATE":

            cursor.execute("""
                UPDATE employees
                SET
                    employee_code=%s,
                    first_name=%s,
                    last_name=%s,
                    dob=%s,
                    doj=%s,
                    project_id=%s,
                    phone=%s,
                    aadhar_number=%s,
                    pan_number=%s,
                    email=%s,
                    comp_mail=%s,
                    gender=%s,
                    department_id=%s,
                    designation_id=%s,
                    reporting_manager_id=%s,
                    location_id=%s,
                    grade_id=%s
                WHERE employee_id=%s
            """, (

                employee_code,
                first_name,
                last_name,
                dob,
                doj,
                project_id,
                phone,
                aadhar_number,
                pan_number,
                email,
                comp_mail,
                gender,
                department_id,
                designation_id,
                reporting_manager_id,
                location_id,
                grade_id,
                employee_id
            ))

            flash("✅ Employee Updated Successfully!", "employee_msg")



        # =========================
        # DELETE
        # =========================

        elif action == "DELETE":

            cursor.execute("""
                UPDATE employees
                SET is_active = FALSE
                WHERE employee_id=%s
            """, (employee_id,))

            flash("✅ Employee Deleted Successfully!", "employee_msg")



        mysql.connection.commit()

    except Exception as e:

        mysql.connection.rollback()

        flash(f"❌ Error: {str(e)}", "employee_msg")

    finally:

        cursor.close()

    return redirect("/admin#employees")





@employee_bp.route("/get_employee_by_code", methods=["POST"])
def get_employee_by_code():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    employee_code = request.form.get("employee_code")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            employee_id,
            first_name,
            last_name,
            dob,
            doj,
            project_id,
            phone,
            aadhar_number,
            pan_number,
            email,
            comp_mail,
            gender,
            department_id,
            designation_id,
            reporting_manager_id,
            location_id,
            grade_id
        FROM employees
        WHERE employee_code=%s
        AND is_active=TRUE
    """, (employee_code,))

    emp = cursor.fetchone()


    cursor.close()

    if emp:

        return {

            "exists": True,

            "employee_id": emp[0],
            "first_name": emp[1],
            "last_name": emp[2],

            "dob": emp[3].strftime("%Y-%m-%d") if emp[3] else "",

            "doj": emp[4].strftime("%Y-%m-%d") if emp[4] else "",

            "project_id": emp[5],

            "phone": str(emp[6]) if emp[6] else "",

            "aadhar_number": emp[7],

            "pan_number": emp[8],

            "email": emp[9],

            "comp_mail": emp[10],

            "gender": emp[11],

            "department_id": emp[12],

            "designation_id": emp[13],

            "reporting_manager_id": emp[14],

             "location_id": emp[15],

            "grade_id": emp[16]

        }

    else:

        return {"exists": False}
    


# ==========================================
# EMPLOYEE DASHBOARD
# ==========================================

@employee_bp.route("/employee")
def employee_dashboard():


    # 🔐 LOGIN CHECK (CHANGED)
    if "email" not in session:
        return redirect("/login")

    email = session["email"]

    cursor = mysql.connection.cursor()

    print("LOGGED EMPLOYEE EMAIL:", email)

    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT 
    e.employee_id,
    e.employee_code,
    e.first_name,
    e.last_name,
    e.dob,
    e.doj,
    e.phone,
    e.email,
    e.comp_mail,
    e.reporting_manager_id,
    e.gender,

    l.location_name,
    g.grade_name,
    p.project_name,
    e.aadhar_number,
    e.pan_number,
    d.department_name,
    e.profile_photo,
                   
    e.resume_file,
    e.resume_path,
                   
    CONCAT(rm.first_name,' ',rm.last_name) AS reporting_manager_name,
    rm.employee_code AS reporting_manager_code,
    rmd.designation_name AS reporting_manager_designation

FROM employees e

LEFT JOIN employees rm
ON e.reporting_manager_id = rm.employee_id
                   
LEFT JOIN tbl_designation rmd
ON rm.designation_id = rmd.designation_id
                   
LEFT JOIN tbl_location l ON e.location_id = l.location_id
                   
LEFT JOIN tbl_grade g ON e.grade_id = g.grade_id
                   
LEFT JOIN tbl_project p ON e.project_id = p.project_id
                   
LEFT JOIN tbl_department d ON e.department_id = d.department_id

WHERE (e.email=%s OR e.comp_mail=%s)
AND e.is_active=TRUE
    """, (email, email))



    emp = cursor.fetchone()

    doj = emp[5]   # joining date index in your query

    experience_text = ""

    if doj:
        today = date.today()
        diff = relativedelta(today, doj)

        years = diff.years
        months = diff.months
        days = diff.days

        if years > 0:
            experience_text += f"{years} Year{'s' if years > 1 else ''} "

        if months > 0:
            experience_text += f"{months} Month{'s' if months > 1 else ''} "

        if years == 0 and months == 0:
            experience_text += f"{days} Day{'s' if days > 1 else ''}"

    print("EMP DATA:", emp)

    if not emp:
        return "Employee record not found. Please contact your admin to ensure your login email matches the email registered in the employee records."
    
    today = date.today()

    emp_dob = emp[4]
    emp_joining = emp[5]

    show_birthday_popup = False
    show_anniversary_popup = False

    if emp_dob:
        show_birthday_popup = (
            emp_dob.month == today.month and
            emp_dob.day == today.day
        )

    if emp_joining:
        show_anniversary_popup = (
            emp_joining.month == today.month and
            emp_joining.day == today.day
        )


    employee_id = emp[0]


    # TDS
    cursor.execute("""
        SELECT t.tds_id, t.form_type, t.quarter, t.financial_year, t.file_name
        FROM tds_certificate t
        WHERE t.employee_id=%s
        ORDER BY t.financial_year DESC, t.quarter ASC
    """, (employee_id,))
    tds_list = cursor.fetchall()


    cursor.execute("""
        SELECT DISTINCT financial_year
        FROM tds_certificate
        ORDER BY financial_year DESC
    """)
    years = [row[0] for row in cursor.fetchall()]

    # Leaves
    cursor.execute("""
        SELECT COUNT(*)
        FROM tbl_leaves
        WHERE employee_id=%s
        AND status='Approved'
    """, (employee_id,))
    total_leaves = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "employee/employee.html",
        emp=emp,
        reporting_manager_name=emp[20],
        reporting_manager_code=emp[21],
        reporting_manager_designation=emp[22],
        total_leaves=total_leaves,
        tds_list=tds_list,
        years=years,
        experience_text=experience_text,
        show_birthday_popup=show_birthday_popup,
        show_anniversary_popup=show_anniversary_popup
    )


ALLOWED_RESUME_EXTENSIONS = {
    "pdf",
    "doc",
    "docx"
}

def allowed_resume(filename):

    return (
        "." in filename and
        filename.rsplit(".",1)[1].lower()
        in ALLOWED_RESUME_EXTENSIONS
    )


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

UPLOAD_RESUME_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads",
    "resume"
)

os.makedirs(UPLOAD_RESUME_FOLDER, exist_ok=True)


@employee_bp.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "email" not in session:
        return redirect("/login")

    file = request.files.get("resume")

    if not file or file.filename == "":
        flash("Select a file.")
        return redirect("/employee")

    if not allowed_resume(file.filename):
        flash("Only PDF/DOC/DOCX allowed.")
        return redirect("/employee")

    if len(file.read()) > 5 * 1024 * 1024:
        flash("Maximum size is 5 MB.")
        return redirect("/employee")

    file.seek(0)

    email = session["email"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            employee_code,
            resume_path
        FROM employees
        WHERE email=%s
        OR comp_mail=%s
    """,(email,email))

    emp = cursor.fetchone()

    if not emp:

        flash("Employee not found.")
        return redirect("/employee")

    employee_code = emp[0]
    old_resume = emp[1]

    # Delete old resume

    if old_resume and os.path.exists(old_resume):

        os.remove(old_resume)

    extension = file.filename.rsplit(".",1)[1].lower()

    filename = secure_filename(
        f"{employee_code}.{extension}"
    )

    filepath = os.path.join(
        UPLOAD_RESUME_FOLDER,
        filename
    )

    file.save(filepath)

    cursor.execute("""
        UPDATE employees
        SET
        resume_file=%s,
        resume_path=%s
        WHERE employee_code=%s
    """,(filename,filepath,employee_code))

    mysql.connection.commit()

    cursor.close()

    flash("Resume uploaded successfully.")

    return redirect("/employee#resume")


@employee_bp.route("/download_resume")
def download_resume():

    if "email" not in session:
        return redirect("/login")

    email = session["email"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
        resume_file,
        resume_path
        FROM employees
        WHERE email=%s
        OR comp_mail=%s
    """,(email,email))

    resume = cursor.fetchone()

    cursor.close()

    # Check database record and physical file
    if (
        not resume
        or not resume[1]
        or not os.path.exists(resume[1])
    ):
        flash("Resume not found.")
        return redirect("/employee#resume")

    return send_file(
        resume[1],
        as_attachment=True,
        download_name=resume[0]
    )




@employee_bp.route("/employee_salary_slip", methods=["POST"])
def employee_salary_slip():

    email = session.get("email")

    if not email:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    # Find employee code of logged-in employee
    cursor.execute("""
        SELECT employee_id, employee_code, first_name, last_name, designation_id
        FROM employees
        WHERE (email=%s OR comp_mail=%s) AND is_active=TRUE
    """, (email, email))

    emp = cursor.fetchone()

    if not emp:
        cursor.close()
        return """
        <script>
        alert("Employee not found");
        history.back();
        </script>
        """

    employee_id_int = emp[0]
    employee_code = emp[1]
    emp_name = f"{emp[2]} {emp[3]}"
    
    # Get designation name
    cursor.execute("SELECT designation_name FROM tbl_designation WHERE designation_id=%s", (emp[4],))
    desig_row = cursor.fetchone()
    designation = desig_row[0] if desig_row else ""

    month = request.form["month"]
    year = int(request.form["year"])

    # ===============================
    # CHECK WHETHER SALARY SHEET EXISTS
    # ===============================

    cursor.execute("""
        SELECT COUNT(*)
        FROM salary_sheet_history
        WHERE salary_month=%s
        AND salary_year=%s
    """, (month, year))

    if cursor.fetchone()[0] == 0:
        cursor.close()
        return """
        <script>
        alert("Salary Sheet Not Uploaded");
        history.back();
        </script>
        """

    # ===============================
    # FETCH EMPLOYEE SALARY
    # ===============================

    cursor.execute("""
        SELECT
            employee_id,
            employee_name,
            designation,
            salary_json
        FROM employee_salary
        WHERE employee_id=%s
        AND salary_month=%s
        AND salary_year=%s
        """, (employee_code, month, year))

    salary_record = cursor.fetchone()

    cursor.close()

    if not salary_record:
        return """
        <script>
        alert("No salary slip found for the selected month and year.");
        history.back();
        </script>
        """

    salary_data = json.loads(salary_record[3])

    deduction_keywords = [
        "tds",
        "loan",
        "pf",
        "esi",
        "deduction",
        "advance",
        "recovery",
        "professional tax"
    ]

    earnings = []
    deductions = []

    for key, value in salary_data.items():
        column_name = str(key).strip().lower()
        column_name = (
            column_name
            .replace(".", "")
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if (
            column_name.startswith("sr")
            or column_name.startswith("serial")
            or column_name in [
                "empno",
                "employeeid",
                "name",
                "employeename",
                "designation",
                "paymentdate",
                "total",
                "payment",
                "netsalary",
                "net",
                "grosssalary",
                "gross",
                "totalearnings",
                "totalearning",
                "totaldeductions",
                "totaldeduction"
            ]
        ):
            continue

        try:
            amount = float(str(value).replace(",", ""))
        except:
            continue

        if amount == 0:
            continue

        is_deduction = any(
            word in column_name
            for word in deduction_keywords
        )

        if is_deduction:
            deductions.append({
                "name": key,
                "amount": amount
            })
        else:
            earnings.append({
                "name": key,
                "amount": amount
            })

    loan_found = False
    for item in deductions:
        if "loan" in item["name"].lower():
            loan_found = True
            break

    if not loan_found:
        deductions.append({
            "name": "Loan",
            "amount": 0
        })

    total_earnings = sum(item["amount"] for item in earnings)
    total_deductions = sum(item["amount"] for item in deductions)
    payment = total_earnings - total_deductions

    try:
        from num2words import num2words
        payment_words = num2words(payment, lang="en_IN").title() + " Rupees Only"
    except:
        payment_words = ""

    import datetime
    return render_template(
        "salary/salary_slip.html",
        employee_id=employee_code,
        name=salary_record[1] if salary_record[1] else emp_name,
        designation=salary_record[2] if salary_record[2] else designation,
        month=month,
        year=year,
        earnings=earnings,
        deductions=deductions,
        total_earnings=total_earnings,
        total_deductions=total_deductions,
        payment=payment,
        payment_words=payment_words,
        payment_date=datetime.datetime.now().strftime("%d-%m-%Y")
    )

from flask import jsonify, request

@employee_bp.route("/search_tds", methods=["POST"])
def search_tds():

    data = request.get_json()
    quarter = data.get("quarter")
    year = data.get("year")

    email = session["email"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT t.tds_id, t.file_name
        FROM tds_certificate t
        JOIN employees e ON e.employee_id = t.employee_id
        WHERE (e.email=%s OR e.comp_mail=%s)
        AND t.quarter=%s
        AND t.financial_year=%s
    """, (email, email, quarter, year))

    row = cursor.fetchone()
    cursor.close()

    if row:
        return jsonify({
            "exists": True,
            "tds_id": row[0],
            "file_name": row[1]
        })

    return jsonify({"exists": False})

@employee_bp.route("/change_employee_password", methods=["POST"])
def change_employee_password():
    if "user_id" not in session:
        return redirect("/login")
        
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    
    if new_password != confirm_password:
        flash("New passwords do not match.", "pwd_error")
        return redirect("/employee#password")
        
    user_id = session["user_id"]
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT password_hash FROM tbl_user WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        flash("User not found.", "pwd_error")
        return redirect("/employee#password")
        
    from werkzeug.security import generate_password_hash, check_password_hash
    
    if not check_password_hash(row[0], current_password):
        cursor.close()
        flash("Incorrect current password.", "pwd_error")
        return redirect("/employee#password")
        
    new_hash = generate_password_hash(new_password)
    
    cursor.execute("UPDATE tbl_user SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
    mysql.connection.commit()
    cursor.close()
    
    flash("Password updated successfully!", "pwd_success")
    return redirect("/employee#password")

