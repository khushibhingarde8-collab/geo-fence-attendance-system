import os 
from flask import Blueprint, render_template, request, redirect, flash, session
from config import mysql
from werkzeug.utils import secure_filename

HOME_GALLERY_FOLDER = "static/home_gallery"
CERTIFICATE_IMAGE_FOLDER = "static/home_certificates/images"
CERTIFICATE_PDF_FOLDER = "static/home_certificates/pdfs"
GALLERY_FOLDER = "static/gallery"
SERVICE_FOLDER = "static/service_uploads"

os.makedirs(HOME_GALLERY_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATE_IMAGE_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATE_PDF_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
os.makedirs(SERVICE_FOLDER, exist_ok=True)

home_bp = Blueprint("home_bp", __name__)

@home_bp.route("/save_home_purpose", methods=["POST"])
def save_home_purpose():

    purpose_id = request.form["id"]
    title = request.form["title"]
    description = request.form["description"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE tbl_home_purpose
        SET title=%s,
            description=%s
        WHERE id=%s
    """,(title,description,purpose_id))

    mysql.connection.commit()
    cursor.close()

    flash("Purpose Updated Successfully")

    return redirect("/admin")

@home_bp.route("/save_engineers_trained", methods=["POST"])
def save_engineers_trained():

    if "user_id" not in session:
        return redirect("/login")

    engineers_trained = request.form["engineers_trained"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE tbl_home_achievement
        SET engineers_trained=%s
        WHERE id=1
    """, (engineers_trained,))

    mysql.connection.commit()
    cursor.close()

    flash("Achievement updated successfully", "home_msg")
    return redirect("/admin#homepage")

@home_bp.route("/save_journey", methods=["POST"])
def save_journey():

    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    journey_id = request.form.get("journey_id")
    year = request.form.get("year")
    title = request.form.get("title")
    description = request.form.get("description")

    cursor = mysql.connection.cursor()

    if action == "INSERT":
        cursor.execute("""
            INSERT INTO tbl_home_journey (year, title, description)
            VALUES (%s,%s,%s)
        """, (year, title, description))

    elif action == "UPDATE":
        cursor.execute("""
            UPDATE tbl_home_journey
            SET year=%s, title=%s, description=%s
            WHERE journey_id=%s
        """, (year, title, description, journey_id))

    elif action == "DELETE":
        cursor.execute("""
            DELETE FROM tbl_home_journey
            WHERE journey_id=%s
        """, (journey_id,))

    mysql.connection.commit()
    cursor.close()

    flash("Journey updated successfully", "home_msg")
    return redirect("/admin#homepage")

@home_bp.route("/save_business_scope", methods=["POST"])
def save_business_scope():

    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    scope_id = request.form.get("scope_id")
    title = request.form.get("title")
    description = request.form.get("description")

    cursor = mysql.connection.cursor()

    if action == "INSERT":
        cursor.execute("""
            INSERT INTO tbl_home_business_scope (title, description)
            VALUES (%s,%s)
        """, (title, description))

    elif action == "UPDATE":
        cursor.execute("""
            UPDATE tbl_home_business_scope
            SET title=%s, description=%s
            WHERE scope_id=%s
        """, (title, description, scope_id))

    elif action == "DELETE":
        cursor.execute("""
            DELETE FROM tbl_home_business_scope
            WHERE scope_id=%s
        """, (scope_id,))

    mysql.connection.commit()
    cursor.close()

    flash("Business scope updated successfully")
    return redirect("/admin#homepage")

# -----------------------------------client page ------------------------------

@home_bp.route("/website-client")
def website_client():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT title, description
        FROM client_content
        LIMIT 1
    """)
    client_content = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM clients
        ORDER BY id DESC
    """)
    clients = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM client_testimonials
        ORDER BY id DESC
    """)
    testimonials = cursor.fetchall()

    cursor.close()

    return render_template(
        "client/client.html",
        client_content=client_content,
        clients=clients,
        testimonials=testimonials
    )

@home_bp.route("/website/update_client_content", methods=["POST"])
def update_website_client_content():

    title = request.form.get("title")
    description = request.form.get("description")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE client_content
        SET title=%s, description=%s
        WHERE id=1
    """, (title, description))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#website_clients")

@home_bp.route("/website/save_client", methods=["POST"])
def save_website_client():

    action = request.form.get("action")

    cursor = mysql.connection.cursor()


    name = (request.form.get("name") or "").strip()
    website = (request.form.get("website") or "").strip()
    cid = request.form.get("client_id")



    if action in ["UPDATE", "DELETE"] and not cid:

        cursor.close()
        return redirect("/admin#website_clients")



    if action == "INSERT":


        if not name:

            cursor.close()

        logo = request.files.get("logo")

        path = ""


        if logo and logo.filename:


            filename = secure_filename(
                logo.filename
            )


            folder = "static/client"

            os.makedirs(
                folder,
                exist_ok=True
            )


            path = os.path.join(
                folder,
                filename
            )


            logo.save(path)


            path = path.replace("\\","/")



        cursor.execute(
            """
            INSERT INTO clients
            (name, logo, website)
            VALUES (%s,%s,%s)
            """,
            (
                name,
                path,
                website
            )
        )




    elif action == "UPDATE":


        logo = request.files.get("logo")


        if logo and logo.filename:


            filename = secure_filename(
                logo.filename
            )


            folder="static/client"


            os.makedirs(
                folder,
                exist_ok=True
            )


            path=os.path.join(
                folder,
                filename
            )


            logo.save(path)


            path=path.replace("\\","/")


            cursor.execute(
                """
                UPDATE clients
                SET name=%s,
                    website=%s,
                    logo=%s
                WHERE id=%s
                """,
                (
                    name,
                    website,
                    path,
                    cid
                )
            )


        else:


            cursor.execute(
                """
                UPDATE clients
                SET name=%s,
                    website=%s
                WHERE id=%s
                """,
                (
                    name,
                    website,
                    cid
                )
            )





    elif action == "DELETE":


        cursor.execute(
            """
            DELETE FROM clients
            WHERE id=%s
            """,
            (cid,)
        )



    mysql.connection.commit()



    cursor.close()



    return redirect("/admin#website_clients")

@home_bp.route("/website/save_client_testimonial", methods=["POST"])
def save_website_client_testimonial():

    action = request.form.get("action")
    cursor = mysql.connection.cursor()

    if action == "INSERT":

        title = request.form.get("title")
        name = request.form.get("name")
        role = request.form.get("role")
        message = request.form.get("message")

        cursor.execute("""
            INSERT INTO client_testimonials(title, name, role, message)
            VALUES (%s, %s, %s, %s)
        """, (title, name, role, message))

    elif action == "DELETE":

        tid = request.form.get("testimonial_id")
        cursor.execute("DELETE FROM client_testimonials WHERE id=%s", (tid,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#website_clients")


@home_bp.route("/save_gallery_image", methods=["POST"])
def save_gallery_image():

    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")
    gallery_id = request.form.get("gallery_id")
    title = request.form.get("title")
    category = request.form.get("category")
    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    if action == "INSERT":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(HOME_GALLERY_FOLDER, filename)
            image.save(filepath)
            filepath = filepath.replace("\\", "/")

            cursor.execute("""
                INSERT INTO tbl_home_gallery (title, category, image_path)
                VALUES (%s,%s,%s)
            """, (title, category, filepath))

    elif action == "UPDATE":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(HOME_GALLERY_FOLDER, filename)
            image.save(filepath)
            filepath = filepath.replace("\\", "/")

            cursor.execute("""
                UPDATE tbl_home_gallery
                SET title=%s, category=%s, image_path=%s
                WHERE gallery_id=%s
            """, (title, category, filepath, gallery_id))

        else:
            cursor.execute("""
                UPDATE tbl_home_gallery
                SET title=%s, category=%s
                WHERE gallery_id=%s
            """, (title, category, gallery_id))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_home_gallery
            WHERE gallery_id=%s
        """, (gallery_id,))

    mysql.connection.commit()
    cursor.close()

    flash("Gallery updated successfully")
    return redirect("/admin#homepage")

@home_bp.route("/save_certificate_home", methods=["POST"])
def save_certificate_home():

    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")
    certificate_id = request.form.get("certificate_id")
    title = request.form.get("title")
    description = request.form.get("description")

    image = request.files.get("image")
    pdf = request.files.get("pdf")
    

    cursor = mysql.connection.cursor()

    if action == "INSERT":

        image_path = ""
        pdf_path = ""

        if image and image.filename:
            image_name = secure_filename(image.filename)
            image_path = os.path.join(CERTIFICATE_IMAGE_FOLDER, image_name)
            image.save(image_path)
            image_path = image_path.replace("\\", "/")

        if pdf and pdf.filename:
            pdf_name = secure_filename(pdf.filename)
            pdf_path = os.path.join(CERTIFICATE_PDF_FOLDER, pdf_name)
            pdf.save(pdf_path)
            pdf_path = pdf_path.replace("\\", "/")

        cursor.execute("""
            INSERT INTO tbl_home_certificate (title, description, image_path, pdf_path)
            VALUES (%s,%s,%s,%s)
        """, (title, description, image_path, pdf_path))

    elif action == "UPDATE":

        cursor.execute("""
            UPDATE tbl_home_certificate
            SET title=%s, description=%s
            WHERE certificate_id=%s
        """, (title, description, certificate_id))

    elif action == "DELETE":

        print("Deleting Certificate ID:", certificate_id)

        cursor.execute("""
            DELETE FROM tbl_home_certificate
            WHERE certificate_id=%s
        """, (certificate_id,))

        print("Rows Deleted:", cursor.rowcount)

    mysql.connection.commit()
    cursor.close()

    flash("Certificate updated successfully")
    return redirect("/admin#homepage")

@home_bp.route("/save_news", methods=["POST"])
def save_news():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    action = request.form.get("action")
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    description = request.form.get("description")
    news_date = request.form.get("news_date")
    external_link = request.form.get("external_link")

    cursor.execute("""
        DELETE FROM tbl_news
        WHERE created_at < (NOW() - INTERVAL 6 MONTH)
    """)

    if action == "INSERT":

        cursor.execute("""
            INSERT INTO tbl_news (title, description, news_date, external_link)
            VALUES (%s,%s,%s,%s)
        """, (title, description, news_date, external_link))

    elif action == "UPDATE":

        cursor.execute("""
            UPDATE tbl_news
            SET title=%s, description=%s, news_date=%s, external_link=%s
            WHERE news_id=%s
        """, (title, description, news_date, external_link, news_id))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_news WHERE news_id=%s
        """, (news_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#news")

@home_bp.route("/save_gallery", methods=["POST"])
def save_gallery():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    action = request.form.get("action")
    gallery_id = request.form.get("gallery_id")
    title = request.form.get("title")
    category = request.form.get("category")
    image = request.files.get("image")

    image_path = ""

    if action == "INSERT":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(GALLERY_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

        cursor.execute("""
            INSERT INTO tbl_gallery (title, category, image_path)
            VALUES (%s,%s,%s)
        """, (title, category, image_path))

    elif action == "UPDATE":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(GALLERY_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

            cursor.execute("""
                UPDATE tbl_gallery
                SET title=%s, category=%s, image_path=%s
                WHERE gallery_id=%s
            """, (title, category, image_path, gallery_id))

        else:
            cursor.execute("""
                UPDATE tbl_gallery
                SET title=%s, category=%s
                WHERE gallery_id=%s
            """, (title, category, gallery_id))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_gallery WHERE gallery_id=%s
        """, (gallery_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#gallery")

@home_bp.route("/gallery")
def gallery():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tbl_gallery
        ORDER BY created_at DESC
    """)

    all_gallery = cursor.fetchall()
    cursor.close()

    return render_template("about/gallery.html", all_gallery=all_gallery)

@home_bp.route("/update_service_content", methods=["POST"])
def update_service_content():

    if "user_id" not in session:
        return redirect("/login")

    content = request.form.get("content")

    cursor = mysql.connection.cursor()

    cursor.execute("DELETE FROM tbl_service_content")

    cursor.execute("""
        INSERT INTO tbl_service_content (content)
        VALUES (%s)
    """, (content,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#service")

@home_bp.route("/save_service", methods=["POST"])
def save_service():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    action = request.form.get("action")
    service_id = request.form.get("service_id")

    title = request.form.get("title")
    description = request.form.get("description")

    image = request.files.get("image")

    image_path = ""

    if action == "INSERT":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(SERVICE_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

        cursor.execute("""
            INSERT INTO tbl_services(title, description, image)
            VALUES(%s, %s, %s)
            """, (title, description, image_path))

    elif action == "UPDATE":

        if image and image.filename:

            filename = secure_filename(image.filename)
            filepath = os.path.join(SERVICE_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

            cursor.execute("""
            UPDATE tbl_services
            SET title=%s,
            description=%s,
            image=%s
            WHERE id=%s
            """, (title, description, image_path, service_id))

        else:

            cursor.execute("""
            UPDATE tbl_services
            SET title=%s,
            description=%s
            WHERE id=%s
            """, (title, description, service_id))

    elif action == "DELETE":

        cursor.execute("DELETE FROM tbl_service_features WHERE service_id=%s", (service_id,))
        cursor.execute("DELETE FROM tbl_service_details WHERE service_id=%s", (service_id,))
        cursor.execute("DELETE FROM tbl_services WHERE id=%s", (service_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#service")

@home_bp.route("/save_testimonial", methods=["POST"])
def save_testimonial():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    action = request.form.get("action")
    tid = request.form.get("testimonial_id")

    name = request.form.get("name")
    message = request.form.get("message")
    image = request.files.get("image")

    image_path = ""

    if action == "INSERT":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(SERVICE_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

        cursor.execute("""
            INSERT INTO tbl_testimonials (name, message, image)
            VALUES (%s,%s,%s)
        """, (name, message, image_path))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_testimonials
            WHERE id=%s
        """, (tid,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#service")

@home_bp.route("/save_team", methods=["POST"])
def save_team():

    if "user_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    action = request.form.get("action")
    team_id = request.form.get("team_id")

    name = request.form.get("name")
    role = request.form.get("role")
    image = request.files.get("image")

    image_path = ""

    if action == "INSERT":

        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join(SERVICE_FOLDER, filename)
            image.save(filepath)
            image_path = filepath.replace("\\", "/")

        cursor.execute("""
            INSERT INTO tbl_team (name, role, image)
            VALUES (%s,%s,%s)
        """, (name, role, image_path))

    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM tbl_team
            WHERE id=%s
        """, (team_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#service")

#  -=========================project page ============================
@home_bp.route("/website_project")
def website_project():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT heading, description
        FROM website_project_page
        LIMIT 1
    """)
    project_page = cursor.fetchone()

    cursor.execute("""
        SELECT logo
        FROM clients
        WHERE logo IS NOT NULL
        AND logo!=''
        ORDER BY id DESC
    """)
    client_logos = cursor.fetchall()

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
    ON p.card_id = c.card_id
    ORDER BY p.project_id DESC
    """)

    website_projects = cursor.fetchall()

    cursor.close()

    return render_template(
    "project/project.html",
    project_page=project_page,
    website_project_pages=project_page,
    client_logos=client_logos,
    website_project_cards=website_project_cards,
    website_projects=website_projects
)

@home_bp.route("/website/save_project_page", methods=["POST"])
def save_project_page():

    heading = request.form.get("heading")
    description = request.form.get("description")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE website_project_page
        SET heading=%s,
            description=%s
        WHERE id=1
    """, (heading, description))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#website-project-management")

@home_bp.route("/save_project_card", methods=["POST"])
def save_project_card():

    action = request.form.get("action")

    cursor = mysql.connection.cursor()

    card_id = request.form.get("card_id")

    title = request.form.get("title")
    description = request.form.get("description")
    icon_class = request.form.get("icon_class")
    slug = request.form.get("slug")

    image = request.files.get("image")

    image_path = None

    if image and image.filename:

        filename = secure_filename(image.filename)

        folder = "static/project/images_project"

        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, filename)

        image.save(path)

        image_path = path.replace("\\","/")

    if action == "INSERT":

        cursor.execute("""
            INSERT INTO website_project_cards
            (title,description,image,icon_class,slug)
            VALUES(%s,%s,%s,%s,%s)
        """,
        (
            title,
            description,
            image_path,
            icon_class,
            slug
        ))

    elif action == "UPDATE":

        if image_path:

            cursor.execute("""
                UPDATE website_project_cards
                SET
                    title=%s,
                    description=%s,
                    image=%s,
                    icon_class=%s,
                    slug=%s
                WHERE card_id=%s
            """,
            (
                title,
                description,
                image_path,
                icon_class,
                slug,
                card_id
            ))

        else:

            cursor.execute("""
                UPDATE website_project_cards
                SET
                    title=%s,
                    description=%s,
                    icon_class=%s,
                    slug=%s
                WHERE card_id=%s
            """,
            (
                title,
                description,
                icon_class,
                slug,
                card_id
            ))

    elif action == "DELETE":

        cursor.execute("""
            DELETE
            FROM website_project_cards
            WHERE card_id=%s
        """,
        (card_id,))

    mysql.connection.commit()

    cursor.close()

    return redirect("/admin#website-project-management")

@home_bp.route("/save_website_project", methods=["POST"])
def save_website_project():

    action = request.form.get("action")

    cursor = mysql.connection.cursor()

    project_id = request.form.get("project_id")
    card_id = request.form.get("card_id")

    project_title = request.form.get("project_title")
    short_description = request.form.get("short_description")
    full_description = request.form.get("full_description")

    team_size = request.form.get("team_size")
    duration = request.form.get("duration")
    technology_used = request.form.get("technology_used")
    client_name = request.form.get("client_name")
    completion_date = request.form.get("completion_date")
    other_details = request.form.get("other_details")


    image = request.files.get("project_image")

    image_path = None


    if image and image.filename:

        filename = secure_filename(image.filename)

        folder = "static/project/images_project"

        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, filename)

        image.save(path)

        image_path = path.replace("\\","/")


    if action == "INSERT":

        cursor.execute("""
            INSERT INTO website_projects
            (
            card_id,
            project_title,
            short_description,
            full_description,
            project_image,
            team_size,
            duration,
            technology_used,
            client_name,
            completion_date,
            other_details
            )

            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """,
        (
            card_id,
            project_title,
            short_description,
            full_description,
            image_path,
            team_size,
            duration,
            technology_used,
            client_name,
            completion_date,
            other_details
        ))



    elif action == "UPDATE":


        if image_path:

            cursor.execute("""
            UPDATE website_projects
            SET
            card_id=%s,
            project_title=%s,
            short_description=%s,
            full_description=%s,
            project_image=%s,
            team_size=%s,
            duration=%s,
            technology_used=%s,
            client_name=%s,
            completion_date=%s,
            other_details=%s

            WHERE project_id=%s

            """,
            (
            card_id,
            project_title,
            short_description,
            full_description,
            image_path,
            team_size,
            duration,
            technology_used,
            client_name,
            completion_date,
            other_details,
            project_id
            ))


        else:

            cursor.execute("""
            UPDATE website_projects
            SET
            card_id=%s,
            project_title=%s,
            short_description=%s,
            full_description=%s,
            team_size=%s,
            duration=%s,
            technology_used=%s,
            client_name=%s,
            completion_date=%s,
            other_details=%s

            WHERE project_id=%s

            """,
            (
            card_id,
            project_title,
            short_description,
            full_description,
            team_size,
            duration,
            technology_used,
            client_name,
            completion_date,
            other_details,
            project_id
            ))



    elif action == "DELETE":

        cursor.execute("""
            DELETE FROM website_projects
            WHERE project_id=%s
        """,
        (project_id,))


    mysql.connection.commit()

    cursor.close()


    return redirect("/admin#website-project-management")

@home_bp.route("/project-list")
def project_list():

    category = request.args.get("category")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            c.title,
            c.slug
        FROM website_project_cards c
        WHERE c.slug=%s
        LIMIT 1
    """,(category,))

    card = cursor.fetchone()

    if card:

        cursor.execute("""
        SELECT
            p.project_id,
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

        JOIN website_project_cards c
        ON p.card_id = c.card_id

        WHERE c.slug=%s

        ORDER BY p.project_id DESC

    """,(category,))
        projects = cursor.fetchall()

    else:

        projects=[]

    cursor.close()

    return render_template(
    "project/projectList.html",
    projects=projects,
    category=card[0] if card else category
)

@home_bp.route("/project-detail")
def project_detail():

    project_id=request.args.get("id")

    cursor=mysql.connection.cursor()

    cursor.execute("""

    SELECT

    p.project_title,
    p.full_description,
    p.project_image,
    p.team_size,
    p.duration,
    p.technology_used,
    p.client_name,
    p.completion_date,
    p.other_details,
    c.title,
    c.slug

    FROM website_projects p

    JOIN website_project_cards c

    ON p.card_id=c.card_id

    WHERE p.project_id=%s

    """,(project_id,))

    project=cursor.fetchone()

    cursor.close()

    return render_template(
        "project/projectDetail.html",
        project=project
    )
