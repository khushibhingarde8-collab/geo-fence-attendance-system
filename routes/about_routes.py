from datetime import datetime
from config import mysql
from MySQLdb.cursors import DictCursor
from flask import Blueprint, render_template, request, flash, redirect

about_bp = Blueprint("about_bp", __name__)


import os
from werkzeug.utils import secure_filename
from flask import current_app

# =====================================
# ABOUT PAGE
# =====================================
@about_bp.route("/about")
def about():

    cursor = mysql.connection.cursor(DictCursor)

    # About Hero
    cursor.execute("""
        SELECT *
        FROM tbl_about_hero
        WHERE status = 1
        ORDER BY id DESC
        LIMIT 1
    """)
    about_hero = cursor.fetchone()

    # Experience
    cursor.execute("""
        SELECT *
        FROM tbl_experience_section
        LIMIT 1
    """)
    experience = cursor.fetchone()

    # Circle Text
    cursor.execute("""
        SELECT *
        FROM tbl_experience_circle_text
        ORDER BY display_order
    """)
    circle_texts = cursor.fetchall()

    # About Profile
    cursor.execute("""
        SELECT *
        FROM tbl_about_profile
        WHERE status = 1
        LIMIT 1
    """)
    profile = cursor.fetchone()

    print("PROFILE =", profile)
    
    # Commitment Section
    cursor.execute("""
    SELECT *
    FROM tbl_commitment
    WHERE status=1
    LIMIT 1
    """)

    commitment = cursor.fetchone()
    
    cursor.execute("""
SELECT *
FROM tbl_team_members
WHERE status=1
ORDER BY display_order,id
    """)

    team_members = cursor.fetchall()

    cursor.close()

    return render_template(
        "about/about.html",
        about_hero=about_hero,
        experience=experience,
        circle_texts=circle_texts,
        profile=profile,
        commitment=commitment,
        team_members=team_members
    )
#==================================
# SAVE / UPDATE ABOUT HERO
#==================================
@about_bp.route("/save_about_hero", methods=["POST"])
def save_about_hero():

    hero_id = request.form.get("hero_id")
    title = request.form.get("title")
    description = request.form.get("description")
    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "about",
        "images_about"
    )

    os.makedirs(upload_folder, exist_ok=True)

    filename = ""

    # If updating, get old image
    if hero_id:
        cursor.execute("""
            SELECT image
            FROM tbl_about_hero
            WHERE id=%s
        """, (hero_id,))
        row = cursor.fetchone()

        if row:
            filename = row[0]

    # Upload new image if selected
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(upload_folder, filename))

    if hero_id:
        cursor.execute("""
            UPDATE tbl_about_hero
            SET
                title=%s,
                description=%s,
                image=%s
            WHERE id=%s
        """, (
            title,
            description,
            filename,
            hero_id
        ))
    else:
        cursor.execute("""
            INSERT INTO tbl_about_hero
            (
                title,
                description,
                image,
                status
            )
            VALUES(%s,%s,%s,1)
        """, (
            title,
            description,
            filename
        ))

    mysql.connection.commit()
    cursor.close()

    flash("Hero saved successfully.")
    return redirect("/admin#aboutHero")

@about_bp.route("/save_about_profile", methods=["POST"])
def save_about_profile():

    description = request.form.get("description")
    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id,image
        FROM tbl_about_profile
        LIMIT 1
    """)

    existing = cursor.fetchone()

    filename = ""

    if existing:
        row_id = existing[0]
        filename = existing[1]
    else:
        row_id = None

    if image and image.filename:

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "about",
            "images_about"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image.save(
            os.path.join(upload_folder, filename)
        )

    if row_id:

        cursor.execute("""
            UPDATE tbl_about_profile
            SET
                description=%s,
                image=%s
            WHERE id=%s
        """,(description,filename,row_id))

    else:

        cursor.execute("""
            INSERT INTO tbl_about_profile
            (
                description,
                image,
                status
            )
            VALUES(%s,%s,1)
        """,(description,filename))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

@about_bp.route("/delete_about_hero/<int:id>")
def delete_about_hero(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_about_hero
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()
    cursor.close()

    flash("Hero deleted successfully.")

    return redirect("/admin#aboutHero")

@about_bp.route("/delete_about_profile/<int:id>")
def delete_about_profile(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_about_profile
        WHERE id=%s
    """,(id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin#aboutProfile")

@about_bp.route("/save_about_commitment", methods=["POST"])
def save_about_commitment():

    heading = request.form.get("heading")
    quote = request.form.get("quote")
    author = request.form.get("author")
    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, image
        FROM tbl_commitment
        LIMIT 1
    """)

    existing = cursor.fetchone()

    filename = ""

    if existing:
        row_id = existing[0]
        filename = existing[1]
    else:
        row_id = None

    if image and image.filename:

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "about",
            "images_about"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image.save(os.path.join(upload_folder, filename))

    if row_id:

        cursor.execute("""
            UPDATE tbl_commitment
            SET
                heading=%s,
                quote=%s,
                author=%s,
                image=%s
            WHERE id=%s
        """, (heading, quote, author, filename, row_id))

    else:

        cursor.execute("""
            INSERT INTO tbl_commitment
            (
                heading,
                quote,
                author,
                image,
                status
            )
            VALUES (%s,%s,%s,%s,1)
        """, (heading, quote, author, filename))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

@about_bp.route("/save_commitment", methods=["POST"])
def save_commitment():

    commitment_id = request.form.get("id")
    heading = request.form.get("heading")
    quote = request.form.get("quote")
    author = request.form.get("author")
    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    filename = ""

    # If updating, get the old image
    if commitment_id:

        cursor.execute("""
            SELECT image
            FROM tbl_commitment
            WHERE id=%s
        """, (commitment_id,))

        existing = cursor.fetchone()

        if existing:
            filename = existing[0]

    # Upload new image
    if image and image.filename:

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "about",
            "images_about"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image.save(
            os.path.join(upload_folder, filename)
        )

    # UPDATE
    if commitment_id:

        cursor.execute("""
            UPDATE tbl_commitment
            SET
                heading=%s,
                quote=%s,
                author=%s,
                image=%s
            WHERE id=%s
        """, (
            heading,
            quote,
            author,
            filename,
            commitment_id
        ))

    # INSERT
    else:

        cursor.execute("""
            INSERT INTO tbl_commitment
            (
                heading,
                quote,
                author,
                image,
                status
            )
            VALUES (%s,%s,%s,%s,1)
        """, (
            heading,
            quote,
            author,
            filename
        ))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

@about_bp.route("/delete_commitment/<int:id>")
def delete_commitment(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_commitment
        WHERE id=%s
    """,(id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

@about_bp.route("/edit_commitment/<int:id>")
def edit_commitment(id):
    return redirect(f"/admin?edit_commitment={id}#commitment")



@about_bp.route("/save_team_member", methods=["POST"])
def save_team_member():

    team_id = request.form.get("id")
    name = request.form.get("name")
    designation = request.form.get("designation")
    description = request.form.get("description")
    experience = request.form.get("experience")
    email = request.form.get("email")
    display_order = request.form.get("display_order")

    image = request.files.get("image")

    cursor = mysql.connection.cursor()

    filename = ""

    # Existing image while updating
    if team_id:

        cursor.execute("""
            SELECT image
            FROM tbl_team_members
            WHERE id=%s
        """, (team_id,))

        existing = cursor.fetchone()

        if existing:
            filename = existing[0]

    # Upload new image
    if image and image.filename:

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "about",
            "images_about"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image.save(
            os.path.join(upload_folder, filename)
        )

    # UPDATE
    if team_id:

        cursor.execute("""
            UPDATE tbl_team_members
            SET
                name=%s,
                designation=%s,
                description=%s,
                experience=%s,
                email=%s,
                display_order=%s,
                image=%s
            WHERE id=%s
        """, (
            name,
            designation,
            description,
            experience,
            email,
            display_order,
            filename,
            team_id
        ))

    # INSERT
    else:

        cursor.execute("""
            INSERT INTO tbl_team_members
            (
                name,
                designation,
                description,
                experience,
                email,
                display_order,
                image,
                status
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,1)
        """, (
            name,
            designation,
            description,
            experience,
            email,
            display_order,
            filename
        ))
        
        print("ID =", request.form.get("id"))
        print(request.form)

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

@about_bp.route("/edit_team_member/<int:id>")
def edit_team_member(id):

    return redirect(f"/admin?edit_team={id}#teamManagement")

@about_bp.route("/delete_team_member/<int:id>")
def delete_team_member(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_team_members
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()
    cursor.close()

    return redirect("/admin")

# =====================================
# GALLERY PAGE
# =====================================
@about_bp.route("/gallery")
def gallery():
    return render_template("about/gallery.html")


# =====================================
# PROFILE PAGE
# =====================================
@about_bp.route("/profile")
def profile():
    return render_template("about/profile.html")