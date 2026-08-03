from flask import Blueprint, request, redirect,flash , render_template
from config import mysql
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

phoenix_bp = Blueprint("phoenix_bp", __name__)

PHOENIX_CATALOG_FOLDER = os.path.join(

    "phoenix_catalogs"
)

os.makedirs(PHOENIX_CATALOG_FOLDER, exist_ok=True)


PHOENIX_CERTIFICATE_FOLDER = "phoenix_certificates"

os.makedirs(PHOENIX_CERTIFICATE_FOLDER, exist_ok=True)


# =========================
# PHOENIX PAGE
# =========================
@phoenix_bp.route("/phoenix")
def phoenix():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            certificate_id,
            title,
            image
        FROM tbl_phoenix_certificate
        WHERE is_active=1
        ORDER BY display_order ASC
    """)

    phoenix_certificates = cursor.fetchall()

    cursor.close()

    return render_template(
        "phoenix/phoenix.html",
        phoenix_certificates=phoenix_certificates
    )

# =========================
# PRODUCT  PAGE
# =========================
@phoenix_bp.route("/product")
def product():

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            catalog_id,
            title,
            pdf_file
        FROM tbl_phoenix_catalog
        WHERE is_active = 1
        ORDER BY display_order ASC
    """)

    phoenix_catalogs = cursor.fetchall()

    cursor.close()

    print(phoenix_catalogs)

    return render_template(
        "phoenix/product.html",
        phoenix_catalogs=phoenix_catalogs
    )


@phoenix_bp.route("/add-phoenix-catalog", methods=["POST"])
def add_phoenix_catalog():

    title = request.form["title"]
    display_order = request.form["display_order"]
    is_active = request.form["is_active"]

    pdf_path = ""

    pdf = request.files.get("pdf_file")

    if pdf and pdf.filename:

        filename = secure_filename(pdf.filename)

        pdf.save(
            os.path.join(PHOENIX_CATALOG_FOLDER, filename)
        )

        pdf_path = filename

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO tbl_phoenix_catalog
        (
            title,
            pdf_file,
            display_order,
            is_active
        )
        VALUES
        (%s,%s,%s,%s)
    """,(
        title,
        pdf_path,
        display_order,
        is_active
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Catalog Added Successfully")

    return redirect("/admin")


@phoenix_bp.route("/update-phoenix-catalog", methods=["POST"])
def update_phoenix_catalog():

    catalog_id = request.form["catalog_id"]
    title = request.form["title"]
    display_order = request.form["display_order"]
    is_active = request.form["is_active"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT pdf_file
        FROM tbl_phoenix_catalog
        WHERE catalog_id=%s
    """,(catalog_id,))

    old_pdf = cursor.fetchone()[0]

    pdf_path = old_pdf

    pdf = request.files.get("pdf_file")

    if pdf and pdf.filename:

        if old_pdf:

            old_file = os.path.join(
                PHOENIX_CATALOG_FOLDER,
                old_pdf
            )

            if os.path.exists(old_file):
                os.remove(old_file)

        filename = secure_filename(pdf.filename)

        pdf.save(
            os.path.join(PHOENIX_CATALOG_FOLDER, filename)
        )

        pdf_path =  filename

    cursor.execute("""
        UPDATE tbl_phoenix_catalog

        SET
            title=%s,
            pdf_file=%s,
            display_order=%s,
            is_active=%s

        WHERE catalog_id=%s
    """,(
        title,
        pdf_path,
        display_order,
        is_active,
        catalog_id
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Catalog Updated Successfully")

    return redirect("/admin")


@phoenix_bp.route("/delete-phoenix-catalog/<int:id>", methods=["POST"])
def delete_phoenix_catalog(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT pdf_file
        FROM tbl_phoenix_catalog
        WHERE catalog_id=%s
    """,(id,))

    row = cursor.fetchone()

    if row and row[0]:

        file_path = os.path.join(
            PHOENIX_CATALOG_FOLDER,
            row[0]
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    cursor.execute("""
        DELETE
        FROM tbl_phoenix_catalog
        WHERE catalog_id=%s
    """,(id,))

    mysql.connection.commit()

    cursor.close()

    flash("Catalog Deleted Successfully")

    return redirect("/admin")


@phoenix_bp.route("/phoenix-catalog/<path:filename>")
def phoenix_catalog_file(filename):
    return send_from_directory(
        PHOENIX_CATALOG_FOLDER,
        filename
    )


# =========================
# PHOENIX-DETAIL PAGE
# =========================
@phoenix_bp.route("/product-detail")
def product_detail():
    return render_template("phoenix/product_detail.html")



@phoenix_bp.route("/add-phoenix-certificate", methods=["POST"])
def add_phoenix_certificate():

    title = request.form["title"]
    display_order = request.form["display_order"]
    is_active = request.form["is_active"]

    image_path = ""

    image = request.files.get("certificate_image")

    if image and image.filename:

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(PHOENIX_CERTIFICATE_FOLDER, filename)
        )

        image_path = filename

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO tbl_phoenix_certificate
        (
            title,
            image,
            display_order,
            is_active
        )
        VALUES
        (%s,%s,%s,%s)
    """, (
        title,
        image_path,
        display_order,
        is_active
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Certificate Added Successfully")

    return redirect("/admin")


@phoenix_bp.route("/update-phoenix-certificate", methods=["POST"])
def update_phoenix_certificate():

    certificate_id = request.form["certificate_id"]
    title = request.form["title"]
    display_order = request.form["display_order"]
    is_active = request.form["is_active"]

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT image
        FROM tbl_phoenix_certificate
        WHERE certificate_id=%s
    """, (certificate_id,))

    old_image = cursor.fetchone()[0]

    image_path = old_image

    image = request.files.get("certificate_image")

    if image and image.filename:

        if old_image:

            old_file = os.path.join(
                PHOENIX_CERTIFICATE_FOLDER,
                old_image
            )

            if os.path.exists(old_file):
                os.remove(old_file)

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(PHOENIX_CERTIFICATE_FOLDER, filename)
        )

        image_path = filename

    cursor.execute("""
        UPDATE tbl_phoenix_certificate
        SET
            title=%s,
            image=%s,
            display_order=%s,
            is_active=%s
        WHERE certificate_id=%s
    """, (
        title,
        image_path,
        display_order,
        is_active,
        certificate_id
    ))

    mysql.connection.commit()

    cursor.close()

    flash("Certificate Updated Successfully")

    return redirect("/admin")

@phoenix_bp.route("/delete-phoenix-certificate/<int:id>", methods=["POST"])
def delete_phoenix_certificate(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT image
        FROM tbl_phoenix_certificate
        WHERE certificate_id=%s
    """, (id,))

    row = cursor.fetchone()

    if row and row[0]:

        image_file = os.path.join(
            PHOENIX_CERTIFICATE_FOLDER,
            row[0]
        )

        if os.path.exists(image_file):
            os.remove(image_file)

    cursor.execute("""
        DELETE FROM tbl_phoenix_certificate
        WHERE certificate_id=%s
    """, (id,))

    mysql.connection.commit()

    cursor.close()

    flash("Certificate Deleted Successfully")

    return redirect("/admin")

@phoenix_bp.route("/phoenix-certificate/<path:filename>")
def phoenix_certificate_file(filename):

    return send_from_directory(
        PHOENIX_CERTIFICATE_FOLDER,
        filename
    )