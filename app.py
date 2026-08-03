from asyncio import events

import os
from flask import Flask, render_template, request, session, flash, redirect, jsonify
from config import init_mysql, mysql
from extensions import mail
from werkzeug.security import generate_password_hash
from flask_mail import Message
from werkzeug.utils import secure_filename
from flask_mail import Mail
from turtle import pd
import num2words
import datetime
from datetime import date
import pandas as pd
from openai import images
import MySQLdb
from MySQLdb.cursors import DictCursor



HOME_GALLERY_FOLDER = "static/home_gallery"
CERTIFICATE_IMAGE_FOLDER = "static/home_certificates/images"
CERTIFICATE_PDF_FOLDER = "static/home_certificates/pdfs"
GALLERY_FOLDER = "static/gallery"
SERVICE_FOLDER = "static/service_uploads"
UPLOAD_PHOTO_FOLDER = "static/profile_photos"

os.makedirs(HOME_GALLERY_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATE_IMAGE_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATE_PDF_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
os.makedirs(SERVICE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_PHOTO_FOLDER, exist_ok=True)


# import routes
from routes.client_routes import client_bp
from routes.project_routes import project_bp
from routes.employee_routes import employee_bp
from routes.service_routes import service_bp
from routes.certificate_routes import certificate_bp
from routes.auth_routes import auth_bp
from routes.leave_management import leave_bp
from routes.tds_bp import tds_bp
from routes.location_bp import location_bp
from routes.grade_bp import grade_bp
from routes.attendance import attendance_bp
from routes.home_routes import home_bp
from routes.phoenix_routes import phoenix_bp
from routes.about_routes import about_bp
from routes.contact_routes import contact_bp
from routes.excel_routes import excel_bp



app = Flask(__name__)
app.secret_key = "secret123"


# ✅ ADD MAIL CONFIG HERE
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vphelwadkar@dbatu.ac.in'
app.config['MAIL_PASSWORD'] = 'fwll rcmt mtwe jxsu'

mail = Mail(app)

UPLOAD_PHOTO_FOLDER = 'static/profile_photos'
if not os.path.exists(UPLOAD_PHOTO_FOLDER):
    os.makedirs(UPLOAD_PHOTO_FOLDER)

# UPLOAD_RESUME_FOLDER = os.path.join(
#     app.root_path,
#     "static",
#     "uploads",
#     "resumes"
# )

# os.makedirs(UPLOAD_RESUME_FOLDER, exist_ok=True)






# @app.route("/service")
# def service():
#     return render_template("service/service.html")

# @app.route("/project")
# def project():
#     return render_template("project/project.html")

# @app.route("/client")
# def client():
#     return render_template("client/client.html")

# @app.route("/phoenix")
# def phoenix():
#     return render_template("phoenix/phoenix.html")

# @app.route("/contact")
# def contact():
#     return render_template("contact/contact.html")



@app.route("/upload_profile_photo", methods=["POST"])
def upload_profile_photo():

    if "email" not in session:
        return redirect("/login")

    file = request.files.get('photo')

    if file and file.filename:

        email = session["email"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT employee_code
            FROM employees
            WHERE email=%s OR comp_mail=%s
        """, (email, email))

        result = cursor.fetchone()

        if result:

            emp_code = result[0]

            filename = secure_filename(f"{emp_code}_{file.filename}")
            filepath = os.path.join(UPLOAD_PHOTO_FOLDER, filename)

            file.save(filepath)

            filepath_url = filepath.replace('\\', '/')

            cursor.execute("""
                UPDATE employees
                SET profile_photo=%s
                WHERE employee_code=%s
            """, (filepath_url, emp_code))

            mysql.connection.commit()

        cursor.close()

    return redirect("/employee")


# ✅ CACHE CONTROL FOR IMAGES
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# ✅ INITIALIZE MAIL (VERY IMPORTANT)
mail.init_app(app)


# database
init_mysql(app)

# register routes
app.register_blueprint(home_bp)
app.register_blueprint(client_bp)
app.register_blueprint(project_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(service_bp)
app.register_blueprint(certificate_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(leave_bp)
app.register_blueprint(tds_bp)
app.register_blueprint(location_bp)
app.register_blueprint(grade_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(phoenix_bp)
app.register_blueprint(about_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(excel_bp)


# ================= ABOUT IMAGE FOLDER =================

ABOUT_FOLDER = os.path.join(app.static_folder, "about", "images_about")
os.makedirs(ABOUT_FOLDER, exist_ok=True)


@app.route("/")
def home():

    cursor = mysql.connection.cursor()

    # Purpose
    cursor.execute("""
        SELECT *
        FROM tbl_home_purpose
        ORDER BY id
    """)
    purposes = cursor.fetchall()


    # Achievement
    cursor.execute("""
        SELECT branches
        FROM tbl_home_achievement
        LIMIT 1
    """)
    achievement = cursor.fetchone()

    branches = achievement[0] if achievement else 0

    from datetime import datetime
    years_experience = datetime.now().year - 2016

    # Journey
    cursor.execute("""
        SELECT *
        FROM tbl_home_journey
        ORDER BY year ASC
    """)
    journeys = cursor.fetchall()

    # Business Scope
    cursor.execute("""
        SELECT *
        FROM tbl_home_business_scope
        ORDER BY scope_id DESC
    """)
    business_scopes = cursor.fetchall()

    # Certificates
    cursor.execute("""
        SELECT *
        FROM tbl_home_certificate
        ORDER BY certificate_id DESC
        LIMIT 2
    """)
    certificates = cursor.fetchall()

    # News
    cursor.execute("""
    SELECT 
        news_id,
        title,
        description,
        news_date,
        external_link,
        news_image
    FROM tbl_news
    ORDER BY news_date DESC
""")
    news_list = cursor.fetchall()


    # Home Gallery
    cursor.execute("""
        SELECT *
        FROM tbl_gallery
        ORDER BY created_at DESC
        LIMIT 3
    """)
    home_gallery = cursor.fetchall()

    # Home Client Logos
    cursor.execute("""
    SELECT id, name, logo, website
    FROM clients
    ORDER BY id DESC
    """)
    
    home_clients = cursor.fetchall()

    import math

    total = len(home_clients)
    per_row = math.ceil(total / 3)

    row1_clients = home_clients[:per_row]
    row2_clients = home_clients[per_row:per_row * 2]
    row3_clients = home_clients[per_row * 2:]

    cursor.close()
    print("PURPOSES =", purposes)
    return render_template(
        "home/home.html",
        purposes=purposes,
        branches=branches,
        years_experience=years_experience,
        journeys=journeys,
        business_scopes=business_scopes,
        certificates=certificates,
        news_list=news_list,
        home_gallery=home_gallery,
        home_clients=home_clients,
        row1_clients=row1_clients,
        row2_clients=row2_clients,
        row3_clients=row3_clients
    )


@app.route("/gallery")
def gallery():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tbl_gallery
        WHERE category='Events'
        ORDER BY created_at DESC
    """)
    events = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM tbl_gallery
        WHERE category='Site Visits'
        ORDER BY created_at DESC
    """)
    site_visits = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM tbl_gallery
        WHERE category='Office Activities'
        ORDER BY created_at DESC
    """)
    office_activities = cursor.fetchall()

    cursor.close()

    return render_template(
        "about/gallery.html",
        events=events,
        site_visits=site_visits,
        office_activities=office_activities
    )
    

@app.route("/update_experience", methods=["POST"])
def update_experience():

    years = request.form["years"]
    title = request.form["title"]

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id FROM tbl_experience_section LIMIT 1")
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE tbl_experience_section
            SET years=%s, title=%s
            WHERE id=%s
        """, (years, title, row[0]))
    else:
        cursor.execute("""
            INSERT INTO tbl_experience_section (years, title)
            VALUES (%s, %s)
        """, (years, title))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#experience")


@app.route("/add_circle_text", methods=["POST"])
def add_circle_text():

    text = request.form["text"]
    order = request.form["display_order"]

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM tbl_experience_circle_text")
    count = cursor.fetchone()[0]

    if count >= 10:
        flash("Maximum 10 points allowed.")
        cursor.close()
        return redirect("/admin#experience")

    cursor.execute("""
        INSERT INTO tbl_experience_circle_text
        (text, display_order)
        VALUES (%s,%s)
    """, (text, order))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#experience")


@app.route("/delete_circle_text/<int:id>")
def delete_circle_text(id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM tbl_experience_circle_text WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#experience")


@app.route("/edit_circle_text/<int:id>", methods=["GET", "POST"])
def edit_circle_text(id):

    cursor = mysql.connection.cursor()

    if request.method == "POST":

        text = request.form["text"]
        order = request.form["display_order"]

        cursor.execute("""
            UPDATE tbl_experience_circle_text
            SET text=%s,
                display_order=%s
            WHERE id=%s
        """, (text, order, id))

        mysql.connection.commit()
        cursor.close()

        return redirect("/admin#experience")

    cursor.execute(
        "SELECT * FROM tbl_experience_circle_text WHERE id=%s",
        (id,)
    )

    point = cursor.fetchone()
    cursor.close()

    return render_template(
        "edit_circle_text.html",
        point=point
    )
    
    


    
@app.route("/save_contact_info", methods=["POST"])
def save_contact_info():

    description = request.form.get("description", "").strip()
    short_address = request.form.get("short_address", "").strip()

    email1 = request.form.get("email1", "").strip()
    email2 = request.form.get("email2", "").strip()

    phone1 = request.form.get("phone1", "").strip()
    phone2 = request.form.get("phone2", "").strip()

    weekday_hours = request.form.get("weekday_hours", "").strip()
    saturday_hours = request.form.get("saturday_hours", "").strip()

    map_link = request.form.get("map_link", "").strip()

    cursor = mysql.connection.cursor()

    # Check if a record already exists
    cursor.execute("SELECT contact_id FROM tbl_contact_info LIMIT 1")
    row = cursor.fetchone()

    if row:

        cursor.execute("""
            UPDATE tbl_contact_info
            SET
                description=%s,
                short_address=%s,
                email1=%s,
                email2=%s,
                phone1=%s,
                phone2=%s,
                weekday_hours=%s,
                saturday_hours=%s,
                map_link=%s
            WHERE contact_id=%s
        """, (
            description,
            short_address,
            email1,
            email2,
            phone1,
            phone2,
            weekday_hours,
            saturday_hours,
            map_link,
            row[0]
        ))

    else:

        cursor.execute("""
            INSERT INTO tbl_contact_info
            (
                description,
                short_address,
                email1,
                email2,
                phone1,
                phone2,
                weekday_hours,
                saturday_hours,
                map_link
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            description,
            short_address,
            email1,
            email2,
            phone1,
            phone2,
            weekday_hours,
            saturday_hours,
            map_link
        ))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#contact")
    
@app.route("/save_social_links", methods=["POST"])
def save_social_links():

    facebook_link = request.form.get("facebook_link", "").strip()
    twitter_link = request.form.get("twitter_link", "").strip()
    whatsapp_link = request.form.get("whatsapp_link", "").strip()
    linkedin_link = request.form.get("linkedin_link", "").strip()

    cursor = mysql.connection.cursor()

    # Check if a record already exists
    cursor.execute("SELECT id FROM tbl_social_links LIMIT 1")
    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE tbl_social_links
            SET
                facebook_link=%s,
                twitter_link=%s,
                whatsapp_link=%s,
                linkedin_link=%s
            WHERE id=%s
        """, (
            facebook_link,
            twitter_link,
            whatsapp_link,
            linkedin_link,
            row[0]
        ))
    else:
        cursor.execute("""
            INSERT INTO tbl_social_links
            (
                facebook_link,
                twitter_link,
                whatsapp_link,
                linkedin_link
            )
            VALUES (%s, %s, %s, %s)
        """, (
            facebook_link,
            twitter_link,
            whatsapp_link,
            linkedin_link
        ))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#contact")

@app.route("/delete_social_links/<int:id>")
def delete_social_links(id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM tbl_social_links WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#contact")

@app.route("/edit_social_links/<int:id>")
def edit_social_links(id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT * FROM tbl_social_links WHERE id=%s",
        (id,)
    )

    social_data = cursor.fetchone()

    cursor.close()

    return redirect("/admin#contact")

@app.route("/save_faq_category", methods=["POST"])
def save_faq_category():

    action = request.form.get("action")
    category_id = request.form.get("category_id")
    category_name = request.form.get("category_name")

    cursor = mysql.connection.cursor()

    if action == "INSERT":

        cursor.execute("""
            INSERT INTO tbl_faq_category(category_name)
            VALUES(%s)
        """, (category_name,))

    elif action == "UPDATE":

        cursor.execute("""
            UPDATE tbl_faq_category
            SET category_name=%s
            WHERE category_id=%s
        """, (category_name, category_id))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_faq_category
            WHERE category_id=%s
        """, (category_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#faq")

@app.route("/save_faq", methods=["POST"])
def save_faq():

    action = request.form.get("action")
    faq_id = request.form.get("faq_id")
    category = request.form.get("category_id")
    question = request.form.get("question")
    answer = request.form.get("answer")

    cursor = mysql.connection.cursor()

    if action == "INSERT":

        cursor.execute("""
            INSERT INTO tbl_faq(category_id,question,answer)
            VALUES(%s,%s,%s)
        """,(category,question,answer))

    elif action == "UPDATE":

        cursor.execute("""
            UPDATE tbl_faq
            SET
                category_id=%s,
                question=%s,
                answer=%s
            WHERE faq_id=%s
        """,(category,question,answer,faq_id))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_faq
            WHERE faq_id=%s
        """,(faq_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#faq")





@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tbl_client WHERE is_active=TRUE ORDER BY client_id DESC")
    clients = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_project ORDER BY project_id DESC")
    projects = cursor.fetchall()

    # ✅ ADD THIS for contact table
    cursor.execute("SELECT * FROM tbl_contact_info ORDER BY contact_id DESC")
    contacts = cursor.fetchall()

    # For table
    cursor.execute("SELECT * FROM tbl_social_links")
    social_links = cursor.fetchall()

     # For form
    cursor.execute("SELECT * FROM tbl_social_links LIMIT 1")
    social_data = cursor.fetchone()


    cursor.execute("""
    SELECT
        e.employee_id,
        e.employee_code,
        e.first_name,
        e.last_name,
        e.dob,
        e.doj,
        e.phone,
        e.aadhar_number,
        e.pan_number,
        e.email,
        e.comp_mail,
        e.gender,
                   
        e.reporting_manager_id,
        CONCAT(rm.first_name,' ',rm.last_name) AS reporting_manager,
       
        e.location_id,
        e.grade_id,
        e.project_id
    FROM employees e

    LEFT JOIN employees rm
    ON e.reporting_manager_id = rm.employee_id

    WHERE e.is_active = TRUE

    ORDER BY e.employee_id DESC
    """)

    employees = cursor.fetchall()


     # ==========================
    # Fetch FAQ Categories
    # ==========================
    cursor.execute("""
        SELECT category_id, category_name
        FROM tbl_faq_category
    """)
    faq_categories = cursor.fetchall()
    
    # ==========================
    # Fetch FAQs
    # ==========================
    
    cursor.execute("""
    SELECT
    f.faq_id,
    f.category_id,
    c.category_name,
    f.question,
    f.answer
    FROM tbl_faq f
    JOIN tbl_faq_category c
    ON f.category_id = c.category_id
    ORDER BY f.faq_id DESC
    """)

    faqs = cursor.fetchall()
    print("FAQs =", faqs)
     # ==========================
    # ADD THIS PART HERE
    # ==========================
    edit_faq = None

    faq_id = request.args.get("edit_faq")

    if faq_id:

        cursor.execute("""
            SELECT
                faq_id,
                category_id,
                question,
                answer
            FROM tbl_faq
            WHERE faq_id=%s
        """, (faq_id,))

        edit_faq = cursor.fetchone()




    # ✅ ADD THESE TWO (THIS IS YOUR MISSING PART)
    cursor.execute("SELECT * FROM tbl_department")
    departments = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_designation")
    designations = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_grade")
    grades = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_location")
    locations = cursor.fetchall()

    cursor.execute("""
    SELECT
        employee_id,
        CONCAT(first_name,' ',last_name) AS manager_name
        FROM employees
        WHERE is_active = TRUE
        ORDER BY first_name
    """)

    managers = cursor.fetchall()


    # counts
    cursor.execute("SELECT COUNT(*) FROM tbl_client WHERE is_active=TRUE")
    client_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active=TRUE")
    employee_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tbl_project")
    project_count = cursor.fetchone()[0]


    # cursor.execute("""
    # SELECT 
    #     e.employee_code,
    #     e.first_name,
    #     e.last_name,
    #     e.dob,
    #     e.doj,
    #     e.grade_id,
    #     e.phone,
    #     e.email,
    #     e.comp_mail,
    #     e.gender,
    #     e.profile_photo,
    
    #     CONCAT(rm.first_name,' ',rm.last_name) AS reporting_manager
    
    # FROM employees e
    
    # LEFT JOIN employees rm
    # ON e.reporting_manager_id = rm.employee_id
    
    # WHERE e.email = %s
    # AND e.is_active = TRUE
    # """, (email,))


    # Fetch pending leaves
    cursor.execute("""
        SELECT l.leave_id, e.first_name, e.last_name, l.start_date, l.end_date, l.reason 
        FROM tbl_leaves l
        JOIN employees e ON l.employee_id = e.employee_id
        WHERE l.status = 'Pending'
    """)
    pending_leaves = cursor.fetchall()

    # ==============================
    # Employee Logins
    # ==============================

    cursor.execute("""
    SELECT
        u.user_id,
        u.email,
        u.is_active
    FROM tbl_user u
    JOIN tbl_user_role ur
        ON u.user_id = ur.user_id
    WHERE ur.role_id = 2
    ORDER BY u.user_id DESC
    """)

    employee_logins = cursor.fetchall()


    # ==============================
    # Admin Logins
    # ==============================

    cursor.execute("""
    SELECT
        u.user_id,
        u.email,
        u.is_active
    FROM tbl_user u
    JOIN tbl_user_role ur
        ON u.user_id = ur.user_id
    WHERE ur.role_id = 1
    ORDER BY u.user_id DESC
    """)

    admin_logins = cursor.fetchall()


    #----------------------------------------------home page 
    # Home Purpose Data
    cursor.execute("""
        SELECT *
        FROM tbl_home_purpose
        ORDER BY id
    """)
    purposes = cursor.fetchall()
    
    # Achievement Section
    from datetime import datetime

# Engineers Trained (manual entry)
    cursor.execute("""
SELECT branches
FROM tbl_home_achievement
LIMIT 1
""")

    achievement = cursor.fetchone()

    if achievement:
        branches = achievement[0]
    else:
        branches = 0

# Years Experience (automatic)
    years_experience = datetime.now().year - 2016

# Projects Completed (from final_database)
    cursor.execute("""
SELECT COUNT(*)
FROM company_portal_2.tbl_project
WHERE project_status = 'completed'
AND is_active = TRUE
""")


    projects_completed = cursor.fetchone()[0]

# Industry Clients
    cursor.execute("""
SELECT COUNT(*)
FROM clients
""")

    industry_clients = cursor.fetchone()[0]

    cursor.execute("""
    SELECT *
    FROM tbl_home_journey
    ORDER BY year ASC
    """)
    journeys = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM tbl_home_business_scope
    ORDER BY scope_id DESC
    """)
    business_scopes = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM tbl_home_certificate
    ORDER BY certificate_id DESC
    LIMIT 2
    """)
    
    certificates = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM tbl_news
    ORDER BY news_date DESC
    """)
    news_list = cursor.fetchall()

    today = date.today().strftime("%Y-%m-%d")

    cursor = mysql.connection.cursor()

    cursor.execute("""
    SELECT *
    FROM tbl_gallery
    ORDER BY created_at DESC
    """)
    gallery_list = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM tbl_gallery
    ORDER BY created_at DESC
    LIMIT 3
    """)
    home_gallery = cursor.fetchall()

    cursor.execute("SELECT content FROM tbl_service_content LIMIT 1")
    service_content = cursor.fetchone()
    service_content = service_content[0] if service_content else ""

    cursor.execute("SELECT * FROM tbl_services ORDER BY id DESC")
    services = cursor.fetchall()


    # Service details (prevent undefined variable)
    try:
        cursor.execute("SELECT * FROM tbl_service_details ORDER BY id DESC")
        service_details = cursor.fetchall()
    except Exception:
        service_details = []

    cursor.execute("SELECT * FROM tbl_testimonials ORDER BY id DESC")
    testimonials = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_team ORDER BY id DESC")
    team = cursor.fetchall()

    # ---------------- WEBSITE CLIENT CONTENT ----------------
    cursor.execute("SELECT id, title, description FROM client_content WHERE id=1")
    row = cursor.fetchone()

    client_content = {
        "title": row[1] if row else "",
        "description": row[2] if row else ""
    }
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tbl_contact_info ORDER BY contact_id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        contact_data = {
        "contact_id": row[0],
        "description": row[1],
        "short_address": row[2],
        "email1": row[3],
        "email2": row[4],
        "phone1": row[5],
        "phone2": row[6],
        "weekday_hours": row[7],
        "saturday_hours": row[8],
        "map_link": row[9]
    }
    else:
     contact_data = {}
     
     # ---------------- CONTACT INFO ----------------
    cursor.execute("""
    SELECT *
    FROM tbl_contact_info
    ORDER BY contact_id DESC
    """)

    contact_list = cursor.fetchall()
    contact_data = contact_list[0] if contact_list else None

    cursor.execute("SELECT * FROM tbl_social_links")
    social_links = cursor.fetchall()

    cursor.execute("SELECT * FROM tbl_social_links LIMIT 1")
    social_data = cursor.fetchone()
    


    # ---------------- WEBSITE CLIENT LOGOS ----------------
    cursor.execute("SELECT id, name, logo, website FROM clients ORDER BY id DESC")
    website_clients = cursor.fetchall()

    # ---------------- WEBSITE TESTIMONIALS ----------------
    cursor.execute("""
        SELECT id, title, name, role, message 
        FROM client_testimonials 
        ORDER BY id DESC
    """)
    client_testimonials = cursor.fetchall()


    #=======================project page=========
    cursor.execute("""
    SELECT *
    FROM website_project_page
    ORDER BY id
    """)

    website_project_pages = cursor.fetchall()
    cursor.execute("""
    SELECT
        p.project_id,
        p.card_id,
        c.title,
        p.project_title,
        p.short_description,
        p.full_description,
        p.project_image,
        p.team_size,
        p.duration,
        p.technology_used,
        p.client_name,
        p.completion_date,
        p.other_details

    FROM website_projects p

    LEFT JOIN website_project_cards c

    ON p.card_id=c.card_id

    ORDER BY p.project_id DESC
    """)

    website_projects = cursor.fetchall()

    cursor.execute("""
    SELECT
    card_id,
    title,
    description,
    image,
    icon_class,
    slug
    FROM website_project_cards
    ORDER BY card_id
    """)

    website_project_cards = cursor.fetchall()




    cursor = mysql.connection.cursor(DictCursor)
    
    cursor.execute("""
    SELECT *
    FROM tbl_about_hero
    WHERE status = 1
    ORDER BY id DESC
    LIMIT 1
    """)

    about_hero = cursor.fetchone()


    # Experience section
    cursor.execute("SELECT * FROM tbl_experience_section LIMIT 1")
    experience = cursor.fetchone()

    # Circle text
    cursor.execute("""
        SELECT * FROM tbl_experience_circle_text
        ORDER BY display_order
    """)
    circle_texts = cursor.fetchall()
    # cursor.close()

    #about profile
    cursor.execute("""
    SELECT *
    FROM tbl_about_profile
    LIMIT 1
       """)

    profile = cursor.fetchone()
    
    cursor.execute("""
    SELECT *
    FROM tbl_commitment
    ORDER BY id DESC
    """)

    commitments = cursor.fetchall()

# ---------------- EDIT COMMITMENT ----------------
    edit_commitment = None

    commitment_id = request.args.get("edit_commitment")

    if commitment_id:

        cursor.execute("""
        SELECT *
        FROM tbl_commitment
        WHERE id=%s
        """, (commitment_id,))

        edit_commitment = cursor.fetchone()
        
   # ---------------- TEAM MEMBERS ----------------
    cursor.execute("""
        SELECT *
        FROM tbl_team_members
        ORDER BY display_order, id
        """)

    team_members = cursor.fetchall()

    print("TEAM MEMBERS =", team_members)


# ---------------- EDIT TEAM ----------------
    edit_team = None

    team_id = request.args.get("edit_team")

    if team_id:

        cursor.execute("""
        SELECT *
        FROM tbl_team_members
        WHERE id=%s
        """, (team_id,))

        edit_team = cursor.fetchone()

    print("EDIT TEAM =", edit_team)



    # ==========================
    # PHOENIX CATALOGS
    # ==========================
    cursor.execute("""
    SELECT *
    FROM tbl_phoenix_catalog
    ORDER BY display_order
    """)
    phoenix_catalogs = cursor.fetchall()


    # ==========================
    # PHOENIX CERTIFICATES
    # ==========================
    cursor.execute("""
    SELECT *
    FROM tbl_phoenix_certificate
    ORDER BY display_order
    """)
    phoenix_certificates = cursor.fetchall()


    cursor.execute("""
        SELECT
            zip_id,
            zip_name,
            uploaded_at
        FROM tds_zip_uploads
        ORDER BY zip_id DESC
        LIMIT 4
    """)

    recent_tds = cursor.fetchall()

    cursor.execute("""
        SELECT salary_month, salary_year, original_file_name, uploaded_date 
        FROM salary_sheet_history 
        ORDER BY salary_year DESC, uploaded_date DESC
    """)
    salary_history = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin/admin.html",
        clients=clients,
        contact_data=contact_data,
        contact_list=contact_list,
        social_links=social_links,
        social_data=social_data,     # <-- ADD THIS
        projects=projects,
        employees=employees,
        departments=departments,      
        designations=designations,
        grades=grades,
        locations=locations,
        client_count=client_count,
        employee_count=employee_count,
        project_count=project_count,
        employee_logins=employee_logins,
        admin_logins=admin_logins,
        pending_leaves=pending_leaves,
        recent_tds=recent_tds,
        salary_history=salary_history,
        managers=managers,
        purposes=purposes,
        branches=branches,
        years_experience=years_experience,
        projects_completed=projects_completed,
        industry_clients=industry_clients,
        journeys=journeys,
        business_scopes=business_scopes,
        certificates=certificates,
        news_list=news_list,
        gallery_list=gallery_list,
        service_content=service_content,
        services=services,
        service_details=service_details,
        website_clients=website_clients,
        testimonials=testimonials,
        client_content=client_content,
        client_testimonials=client_testimonials,
        contacts=contacts,
        faq_categories=faq_categories,
        edit_faq=edit_faq,
        phoenix_catalogs=phoenix_catalogs,
        phoenix_certificates=phoenix_certificates,
        faqs=faqs,
        website_project_pages=website_project_pages,
        website_projects=website_projects,
        website_project_cards=website_project_cards,
        experience=experience,
        circle_texts=circle_texts,
        profile=profile,
        commitments=commitments,
        today=today,
        edit_commitment=edit_commitment,
        team_members=team_members,
        edit_team=edit_team
    )



@app.route("/edit_contact/<int:id>")
def edit_contact(id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT * FROM tbl_contact_info WHERE contact_id=%s",
        (id,)
    )

    contact_data = cursor.fetchone()

    cursor.close()

    # Store id in session or pass via query string if you want to populate the form.
    return redirect("/admin#contact")

@app.route("/delete_contact/<int:id>")
def delete_contact(id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM tbl_contact_info WHERE contact_id=%s",
        (id,)
    )

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#contact")


@app.route("/add_faq", methods=["POST"])
def add_faq():

    category=request.form["category_id"]
    question=request.form["question"]
    answer=request.form["answer"]

    cursor=mysql.connection.cursor()

    cursor.execute("""

    INSERT INTO tbl_faq
    (
        category_id,
        question,
        answer
    )

    VALUES(%s,%s,%s)

    """,(category,question,answer))

    mysql.connection.commit()

    cursor.close()

    return redirect("/admin#faq")


    
@app.route("/update_faq/<int:id>", methods=["POST"])
def update_faq(id):

    category = request.form["category_id"]
    question = request.form["question"]
    answer = request.form["answer"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE tbl_faq
        SET
            category_id=%s,
            question=%s,
            answer=%s
        WHERE faq_id=%s
    """, (category, question, answer, id))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#faq")

@app.route("/delete_faq/<int:id>")
def delete_faq(id):

    print("Deleting FAQ ID:", id)

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_faq
        WHERE faq_id=%s
    """, (id,))

    print("Rows Deleted:", cursor.rowcount)

    mysql.connection.commit()

    cursor.close()

    return redirect("/admin#faq")



@app.route("/service/<service_name>")
def service(service_name):
    service = service.get(service_name)

    if not service:
        return "Service not found", 404

    return render_template("service.html", service=service)





@app.route("/apply_leave", methods=["POST"])
def apply_leave():
    if "user_id" not in session:
        return redirect("/login")

    from datetime import date, datetime

    start_date = request.form['start_date']
    end_date   = request.form['end_date']
    reason     = request.form['reason']
    leave_type = request.form.get('leave_type', 'Casual')

    email = session.get('email')

    cursor = mysql.connection.cursor()

    # ── Get employee_id from email ──
    cursor.execute("""
    SELECT
        employee_id,
        first_name,
        last_name,
        reporting_manager_id
    FROM employees
    WHERE email=%s
    AND is_active=TRUE
    """, (email,))


    emp = cursor.fetchone()

    if not emp:
        flash("❌ Employee not found.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    employee_id = emp[0]
    employee_name = f"{emp[1]} {emp[2]}"
    manager_id = emp[3]

    manager_email = None

    if manager_id:
        cursor.execute("""
            SELECT comp_mail
            FROM employees
            WHERE employee_id=%s
        """, (manager_id,))
    
        mgr = cursor.fetchone()
    
        if mgr:
            manager_email = mgr[0]

    cursor.execute("""
        SELECT comp_mail
        FROM employees
        WHERE employee_id=%s
    """, (manager_id,))

    manager = cursor.fetchone()

    # ── Parse dates ──
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d").date()
        ed = datetime.strptime(end_date,   "%Y-%m-%d").date()
    except ValueError:
        flash("❌ Invalid date format.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    today = date.today()

    # ── Validation 1: Start must not be in the past ──
    if sd < today:
        flash("❌ Start date cannot be in the past.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    # ── Validation 2: End must be >= Start ──
    if ed < sd:
        flash("❌ End date cannot be before start date.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    # ── Calculate days (excluding weekends) ──
    from datetime import timedelta
    total_days = 0
    current = sd
    while current <= ed:
        if current.weekday() < 5:   # Mon–Fri only
            total_days += 1
        current += timedelta(days=1)

    if total_days == 0:
        flash("❌ No working days in selected range.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    # ── Validation 3: Leave balance (max 12 per year) ──
    cursor.execute("""
        SELECT COALESCE(SUM(DATEDIFF(end_date, start_date) + 1), 0)
        FROM tbl_leaves
        WHERE employee_id = %s
          AND status = 'Approved'
          AND YEAR(start_date) = %s
    """, (employee_id, sd.year))
    used = cursor.fetchone()[0] or 0
    remaining = 12 - used

    if total_days > remaining:
        flash(f"❌ Insufficient leave balance. You have {remaining} day(s) left.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    # ── Validation 4: No overlapping pending/approved leaves ──
    cursor.execute("""
        SELECT leave_id FROM tbl_leaves
        WHERE employee_id = %s
          AND status IN ('Pending', 'Approved')
          AND NOT (end_date < %s OR start_date > %s)
    """, (employee_id, start_date, end_date))
    overlap = cursor.fetchone()
    if overlap:
        flash("❌ You already have a leave request for these dates.", "leave_msg")
        cursor.close()
        return redirect("/employee#leave")

    # ── Insert leave ──
    cursor.execute("""
        INSERT INTO tbl_leaves (employee_id, leave_type, start_date, end_date, total_days, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (employee_id, leave_type, start_date, end_date, total_days, reason))

    mysql.connection.commit()

    if manager:

        manager_email = manager[0]

        msg = Message(
            subject="New Leave Request",
            sender=app.config['MAIL_USERNAME'],
            recipients=[manager_email]
        )

        msg.body = f"""
    Employee: {employee_name}

    Leave Type: {leave_type}

    Start Date: {start_date}
    End Date: {end_date}

    Reason:
    {reason}

    Please login and approve/reject this leave request.
    """

        mail.send(msg)

    cursor.close()

    flash(f"✅ Leave applied for {total_days} working day(s). Status: Pending.", "leave_msg")
    return redirect("/employee#leave")




@app.route("/save_department", methods=["POST"])
def save_department():

    action = request.form.get("action")
    dept_id = request.form.get("department_id")
    name = request.form.get("department_name")

    cur = mysql.connection.cursor()

    if action == "INSERT":
        cur.execute("INSERT INTO tbl_department (department_name) VALUES (%s)", (name,))

    elif action == "UPDATE":
        cur.execute("UPDATE tbl_department SET department_name=%s WHERE department_id=%s", (name, dept_id))

    elif action == "DELETE":
        cur.execute("DELETE FROM tbl_department WHERE department_id=%s", (dept_id,))

    mysql.connection.commit()
    cur.close()

    flash(f"Department {action.lower()}ed successfully!", "dept_desig_msg")
    return redirect("/admin#department-designation")   # go back to admin page


@app.route("/save_designation", methods=["POST"])
def save_designation():

    action = request.form.get("action")
    desig_id = request.form.get("designation_id")
    name = request.form.get("designation_name")

    cur = mysql.connection.cursor()

    if action == "INSERT":
        cur.execute("INSERT INTO tbl_designation (designation_name) VALUES (%s)", (name,))

    elif action == "UPDATE":
        cur.execute("""
            UPDATE tbl_designation 
            SET designation_name=%s 
            WHERE designation_id=%s
        """, (name, desig_id))

    elif action == "DELETE":
        cur.execute("DELETE FROM tbl_designation WHERE designation_id=%s", (desig_id,))

    mysql.connection.commit()
    cur.close()

    flash(f"Designation {action.lower()}ed successfully!", "dept_desig_msg")
    return redirect("/admin#department-designation")




@app.route("/add_employee_login", methods=["POST"])
def add_employee_login():

    if "user_id" not in session:
        return redirect("/login")

    email = request.form["email"]
    password = request.form["password"]
    role_id = request.form.get("role_id", 2)

    cursor = mysql.connection.cursor()

    # ✅ Look up the employee from the employees table to ensure they exist
    cursor.execute("""
        SELECT employee_id, CONCAT(first_name,' ',last_name), comp_mail, email
        FROM employees
        WHERE (comp_mail = %s OR email = %s) AND is_active = TRUE
    """, (email, email))

    emp = cursor.fetchone()

    if not emp:
        cursor.close()
        flash("❌ Employee not found. Please ensure the email matches an active employee record.", "login_msg")
        return redirect("/admin#emplogin")

    login_email = email
    emp_name = emp[1]

    # ✅ Check if login already exists
    cursor.execute("SELECT user_id FROM tbl_user WHERE email = %s", (login_email,))
    if cursor.fetchone():
        cursor.close()
        flash(f"❌ A login for {login_email} already exists.", "login_msg")
        return redirect("/admin#emplogin")

    # 🔐 hash password
    hashed_password = generate_password_hash(password)

    # ✅ insert into tbl_user
    cursor.execute("""
        INSERT INTO tbl_user(email, password_hash)
        VALUES(%s, %s)
    """, (login_email, hashed_password))

    user_id = cursor.lastrowid

    # ✅ assign role
    cursor.execute("""
        INSERT INTO tbl_user_role(user_id, role_id)
        VALUES(%s, %s)
    """, (user_id, role_id))

    mysql.connection.commit()

    # ✅ 📧 SEND EMAIL
    try:
        msg = Message(
            subject="Your PCE Portal Login Credentials",
            sender=app.config['MAIL_USERNAME'],
            recipients=[login_email]
        )

        msg.body = f"""Dear {emp_name},

Your employee login account has been created on the PCE Portal.

Login Email: {login_email}
Password: {password}

Please login here: {request.host_url.rstrip('/')}/login

For security, please change your password after first login.

Regards,
PCE Admin Team
        """

        mail.send(msg)
        flash(f"✅ Login created for {emp_name} ({login_email}) and credentials sent by email!", "login_msg")
    except Exception as e:
        flash(f"✅ Login created for {emp_name} ({login_email}), but email could not be sent: {str(e)}", "login_msg")

    cursor.close()
    return redirect("/admin#emplogin")


@app.route("/add_admin_login", methods=["POST"])
def add_admin_login():

    if "user_id" not in session:
        return redirect("/login")

    email    = request.form["email"]
    password = request.form["password"]
    role_id  = request.form.get("role_id", 1)   # default role = Admin

    cursor = mysql.connection.cursor()

    # Check if login already exists
    cursor.execute("SELECT user_id FROM tbl_user WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        flash(f"❌ A login for {email} already exists.", "login_msg")
        return redirect("/admin#emplogin")

    # Hash password
    hashed_password = generate_password_hash(password)

    # Insert into tbl_user
    cursor.execute("""
        INSERT INTO tbl_user(email, password_hash)
        VALUES(%s, %s)
    """, (email, hashed_password))

    user_id = cursor.lastrowid

    # Assign role (Admin = 1)
    cursor.execute("""
        INSERT INTO tbl_user_role(user_id, role_id)
        VALUES(%s, %s)
    """, (user_id, role_id))

    mysql.connection.commit()
    cursor.close()

    flash(f"✅ Admin login created for {email} successfully!", "login_msg")
    return redirect("/admin#emplogin")




@app.route("/update_leave/<int:leave_id>/<status>")
def update_leave(leave_id, status):
    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE tbl_leaves SET status = %s WHERE leave_id = %s", (status, leave_id))
    mysql.connection.commit()
    cursor.close()

    flash(f"Leave {status}!", "leave_msg")
    return redirect("/admin#leaves")
    

@app.route("/delete_login/<int:user_id>")
def delete_login(user_id):
    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()
    
    # Delete from user_role first (foreign key)
    cursor.execute("DELETE FROM tbl_user_role WHERE user_id = %s", (user_id,))
    # Delete from user
    cursor.execute("DELETE FROM tbl_user WHERE user_id = %s", (user_id,))
    
    mysql.connection.commit()
    cursor.close()
    
    flash("Login account deleted!", "login_msg")
    return redirect("/admin#emplogin")


   



@app.route("/delete_profile_photo", methods=["POST"])
def delete_profile_photo():

    if "email" not in session:
        return redirect("/login")

    email = session["email"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT employee_code, profile_photo
        FROM employees
        WHERE email=%s OR comp_mail=%s
    """, (email, email))

    emp = cursor.fetchone()

    if emp and emp[1]:

        # Delete file from folder
        photo_path = emp[1]

        if os.path.exists(photo_path):
            os.remove(photo_path)

        # Remove path from database
        cursor.execute("""
            UPDATE employees
            SET profile_photo=NULL
            WHERE employee_code=%s
        """, (emp[0],))

        mysql.connection.commit()

    cursor.close()

    flash("Profile photo deleted successfully.")
    return redirect("/employee")



# ==========================================
# MONTHLY ATTENDANCE REPORT PAGE
# ==========================================
@app.route("/attendance_report")
def attendance_report():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "attendance/attendance_report.html"
    )




#======salary=====

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= MONTH MAP =================

month_map = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}


# salary slip#

@app.route('/upload_salary_sheet', methods=['POST'])
def upload_salary_sheet():

    try:

        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        file = request.files['salary_file']

        month = request.form['salary_month']
        year = int(request.form['salary_year'])

        selected_month = month_map[month]

        if year > current_year:

            return """
            <script>
            alert("Future year upload not allowed");
            history.back();
            </script>
            """

        if year == current_year and selected_month > current_month:

            return """
            <script>
            alert("Future month upload not allowed");
            history.back();
            </script>
            """
               

        cursor = mysql.connection.cursor()

        original_file_name = file.filename

        # ── NAMING CONVENTION CHECK ──────────────────────────────────────
        import re
        valid_months = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]
        name_without_ext = os.path.splitext(original_file_name)[0]
        pattern = re.compile(
            r'^Salary_(' + '|'.join(valid_months) + r')_(\d{4})$',
            re.IGNORECASE
        )
        match = pattern.match(name_without_ext)

        if not match:
            cursor.close()
            return """
            <script>
            alert("Invalid file name.\\nFile must be named as: Salary_Month_Year.xlsx\\nExample: Salary_June_2026.xlsx");
            history.back();
            </script>
            """

        file_month = match.group(1).capitalize()
        file_year  = int(match.group(2))

        if file_month != month:
            cursor.close()
            return f"""
            <script>
            alert("File name month '{file_month}' does not match selected month '{month}'.\\nPlease rename the file or select the correct month.");
            history.back();
            </script>
            """

        if file_year != year:
            cursor.close()
            return f"""
            <script>
            alert("File name year '{file_year}' does not match selected year '{year}'.\\nPlease rename the file or select the correct year.");
            history.back();
            </script>
            """
        # ── END NAMING CONVENTION CHECK ──────────────────────────────────

        cursor.execute("""
            SELECT id
            FROM salary_sheet_history
            WHERE original_file_name=%s
        """, (original_file_name,))

        if cursor.fetchone():
            cursor.close()
            return """
            <script>
            alert("File with the same name already exists.");
            history.back();
            </script>
            """

        cursor.execute("""
            SELECT id
            FROM salary_sheet_history
            WHERE salary_month=%s
            AND salary_year=%s
        """, (month, year))

        if cursor.fetchone():

            cursor.close()

            return """
            <script>
            alert("Salary sheet already uploaded");
            history.back();
            </script>
            """

        filename = f"salary_{month}_{year}.xlsx"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(filepath)

        df = pd.read_excel(filepath, sheet_name=0)

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        emp_col, name_col, desig_col = None, None, None
        for col in df.columns:
            clean_col = str(col).lower().replace(" ", "").replace("_", "").replace(".", "")
            if clean_col in ["empno", "empid", "employeeid", "employeeno", "employeecode"]:
                emp_col = col
            elif clean_col in ["name", "employeename", "fullname", "empname"]:
                name_col = col
            elif clean_col in ["designation", "role", "position", "title"]:
                desig_col = col

        if not emp_col:
            cursor.close()
            return """
            <script>
            alert("Could not find Employee ID column in the uploaded sheet.");
            history.back();
            </script>
            """

        cursor.execute("""
            INSERT INTO salary_sheet_history(
                salary_month,
                salary_year,
                file_name,
                original_file_name,
                uploaded_date
            )
            VALUES(%s,%s,%s,%s,NOW())
        """, (month, year, filename, original_file_name))

        for _, row in df.iterrows():

            employee_id = str(
                row.get(emp_col, "")
            ).strip()

            if employee_id == "" or employee_id.lower() == "nan":
                continue

            # Normalize to uppercase for consistent matching
            employee_id = employee_id.upper()

            employee_name = str(
                row.get(name_col, "")
            ).strip() if name_col else ""

            designation = str(
                row.get(desig_col, "")
            ).strip() if desig_col else ""

            salary_data = {}

            for col in df.columns:

                value = row[col]

                if pd.isna(value):
                    value = ""

                salary_data[col] = str(value)

            cursor.execute("""
                INSERT IGNORE INTO employee_salary(
                    employee_id,
                    employee_name,
                    designation,
                    salary_month,
                    salary_year,
                    salary_json
                )
                VALUES(%s,%s,%s,%s,%s,%s)
            """, (
                employee_id,
                employee_name,
                designation,
                month,
                year,
                json.dumps(salary_data)
            ))

        mysql.connection.commit()

        cursor.close()

        return """
        <script>
        alert("Salary Sheet Uploaded Successfully");
        history.back();
        </script>
        """

    except Exception as e:

        error_msg = str(e).replace('"', "'").replace('\n', ' ')
        return f"""
        <script>
        alert("Error: {error_msg}");
        history.back();
        </script>
        """

# ================= GENERATE SALARY SLIP =================

import json

@app.route('/generate_salary_slip', methods=['POST'])
def generate_salary_slip():

    employee_id = request.form["employee_id"].strip()

#     email = session.get("email")

#     cursor = mysql.connection.cursor()

#     cursor.execute("""
# SELECT employee_code
# FROM employees
# WHERE email=%s
# OR comp_mail=%s
# """, (email, email))

#     row = cursor.fetchone()

#     if not row:
#         cursor.close()
#         return """
#         <script>
#         alert("Employee not found");
#         history.back();
#         </script>
#         """

#     employee_id = row[0]

    month = request.form["month"]
    year = int(request.form["year"])

    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    selected_month = month_map[month]

    if year > current_year:
        return """
        <script>
        alert('Future year not allowed');
        history.back();
        </script>
        """

    if year == current_year and selected_month > current_month:
        return """
        <script>
        alert('Future month not allowed');
        history.back();
        </script>
        """

    cursor = mysql.connection.cursor()

    # CHECK SHEET EXISTS

    cursor.execute("""
        SELECT COUNT(*)
        FROM salary_sheet_history
        WHERE salary_month=%s
        AND salary_year=%s
    """, (month, year))

    sheet_count = cursor.fetchone()[0]

    if sheet_count == 0:
        cursor.close()
        return """
        <script>
        alert('Salary Sheet Deleted Or Not Uploaded');
        history.back();
        </script>
        """

    # FETCH EMPLOYEE

    cursor.execute("""
        SELECT
            employee_id,
            employee_name,
            designation,
            salary_json
        FROM employee_salary
        WHERE UPPER(employee_id)=UPPER(%s)
        AND salary_month=%s
        AND salary_year=%s
    """, (employee_id, month, year))

    emp = cursor.fetchone()

    cursor.close()

    if not emp:
        return """
        <script>
        alert('Salary Slip Not Found');
        history.back();
        </script>
        """

    salary_data = json.loads(emp[3])

    ignore_columns = [
        "Employee ID",
        "EmpNo",
        "Name",
        "Employee Name",
        "Designation",
        "Payment Date",
        "Total",
        "Payment",
        "Sr No",
        "SR NO",
        "Sr. No",
        "S.No",
        "Sno",
        "Serial No",
        "Serial Number"
    ]

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

    # =====================================================
    # PROCESS EXCEL COLUMNS
    # =====================================================

    for key, value in salary_data.items():
        # Skip non-salary columns
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

        # Skip blank or zero values
        if amount == 0:
            continue

        # Check deduction
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

    # =====================================================
    # CALCULATE TOTALS DYNAMICALLY
    # =====================================================
    total_earnings = sum(item["amount"] for item in earnings)
    total_deductions = sum(item["amount"] for item in deductions)
    payment = total_earnings - total_deductions

    try:
        payment_words = (
            num2words.num2words(payment, lang="en_IN").title()
            + " Rupees Only"
        )
    except:
        payment_words = ""

    return render_template(
        "salary/salary_slip.html",
        employee_id=emp[0],
        name=emp[1],
        designation=emp[2],
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


@app.route('/delete_salary_sheet', methods=['POST'])
def delete_salary_sheet():

    try:

        month = request.form.get("delete_month")
        year = request.form.get("delete_year")

        if not month or not year:

            return jsonify({
                "status": "error",
                "message": "Month and Year are required"
            })

        year = int(year)

        print("DELETE MONTH =", month)
        print("DELETE YEAR =", year)

        cursor = mysql.connection.cursor()

        # Delete employee salary records

        cursor.execute("""
            DELETE FROM employee_salary
            WHERE salary_month=%s
            AND salary_year=%s
        """, (month, year))

        print("EMPLOYEE SALARY DELETED =", cursor.rowcount)

        # Delete history

        cursor.execute("""
            DELETE FROM salary_sheet_history
            WHERE salary_month=%s
            AND salary_year=%s
        """, (month, year))

        print("SALARY HISTORY DELETED =", cursor.rowcount)

        mysql.connection.commit()

        cursor.close()

        # Delete physical Excel file

        filename = f"salary_{month}_{year}.xlsx"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if os.path.exists(filepath):

            os.remove(filepath)

            print("FILE DELETED =", filepath)

        else:

            print("FILE NOT FOUND =", filepath)

        return """
            <script>
            alert("Salary Sheet Deleted Successfully");
            window.location.href="/admin";
            </script>
            """

    except Exception as e:

        print("DELETE ERROR =", str(e))

        return """
            <script>
            alert("Salary Sheet already uploaded");
            history.back();
            </script>
            """  







from scheduler import start_scheduler

start_scheduler()

print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True) 