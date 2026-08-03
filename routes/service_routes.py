# from pyexpat import features

from flask import Blueprint, request, redirect, flash, session, render_template
from streamlit import image
from config import mysql

service_bp = Blueprint("service_bp", __name__)

# =========================
# SERVICE PAGE
# =========================
@service_bp.route("/service")
def service():

    cursor = mysql.connection.cursor()

    # Header Content
    cursor.execute("""
        SELECT content
        FROM tbl_service_content
        ORDER BY id DESC
        LIMIT 1
    """)
    service_content = cursor.fetchone()

    # Service Cards
    cursor.execute("""
    SELECT id, title, description, image
    FROM tbl_services
    ORDER BY id ASC
    """)
    services = cursor.fetchall()

    # Testimonials
    cursor.execute("""
        SELECT id, name, message, image
        FROM tbl_testimonials
        ORDER BY id DESC
    """)
    testimonials = cursor.fetchall()

    cursor.close()

    return render_template(
        "service/service.html",
        service_content=service_content,
        services=services,
        testimonials=testimonials
    )


# =========================
# SERVICE DETAIL PAGE
# =========================
@service_bp.route("/service-detail/<int:service_id>")
def service_detail(service_id):

    cursor = mysql.connection.cursor()

    # SERVICE BASIC INFO
    cursor.execute("""
        SELECT id, title, description
        FROM tbl_services        
        WHERE id = %s
    """, (service_id,))
    service = cursor.fetchone()

    # SERVICE DETAILS (LONG DESCRIPTION + IMAGE)
    cursor.execute("""
        SELECT long_description, image
        FROM tbl_service_details
        WHERE service_id = %s
    """, (service_id,))
    details = cursor.fetchone()

    # SERVICE FEATURES
    cursor.execute("""
        SELECT feature
        FROM tbl_service_features
        WHERE service_id = %s
    """, (service_id,))
    features = cursor.fetchall()

    cursor.close()

    return render_template(
        "service/serviceDetail.html",
        service=service,
        details=details,
        features=features
    )
# =========================
# API (Optional)
# =========================
@service_bp.route("/api/service-detail/<int:service_id>")
def service_detail_api(service_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
SELECT
    d.id,
    s.title,
    d.long_description,
    d.image,
    d.service_id
FROM tbl_service_details d
JOIN tbl_services s
    ON d.service_id = s.id
    ORDER BY d.id DESC
    """)

    service_details = cursor.fetchall()

    if not service_details:
        cursor.close()
        return {"error": "Service details not found"}, 404

    cursor.execute("""
        SELECT feature
        FROM tbl_service_features
        WHERE service_id = %s
    """, (service_id,))



    features = cursor.fetchall()

    cursor.close()

    print("Service ID:", service_id)
    print("Service:", service)
    print("Features:", features)

    return {
        "service": service,
        "features": features
    }

import os
from werkzeug.utils import secure_filename

@service_bp.route("/save_service_detail", methods=["POST"])
def save_service_detail():

    service_id = request.form.get("service_id")
    long_description = request.form.get("long_description")

    image = ""

    image_file = request.files.get("image")

    if image_file and image_file.filename:

        filename = secure_filename(image_file.filename)

        upload_folder = os.path.join("static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        image_file.save(os.path.join(upload_folder, filename))

        image = "static/uploads/" + filename

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id
        FROM tbl_service_details
        WHERE service_id=%s
    """, (service_id,))

    exists = cursor.fetchone()

    if exists:

        if image:
            cursor.execute("""
                UPDATE tbl_service_details
                SET long_description=%s,
                    image=%s
                WHERE service_id=%s
            """, (
                long_description,
                image,
                service_id
            ))
        else:
            cursor.execute("""
                UPDATE tbl_service_details
                SET long_description=%s
                WHERE service_id=%s
            """, (
                long_description,
                service_id
            ))

    else:

        cursor.execute("""
            INSERT INTO tbl_service_details
            (service_id, long_description, image)
            VALUES(%s, %s, %s)
        """, (
            service_id,
            long_description,
            image
        ))

    mysql.connection.commit()
    cursor.close()

    flash("Service Detail Saved", "success")

    return redirect("/admin")

@service_bp.route("/save_features", methods=["POST"])
def save_features():
    
    print("🔥 SAVE FEATURES ROUTE HIT")
    print("FORM DATA:", request.form)

    service_id = request.form.get("service_id")
    features = request.form.getlist("feature")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_service_features
        WHERE service_id=%s
    """, (service_id,))

    for feature in features:
        feature = feature.strip()

        if feature != "":
            cursor.execute("""
                INSERT INTO tbl_service_features (service_id, feature)
                VALUES (%s, %s)
            """, (service_id, feature))

    mysql.connection.commit()
    cursor.close()

    flash("Features Saved", "success")
    return redirect("/admin")
# =========================
# SAVE SERVICE
# =========================
@service_bp.route("/save_service", methods=["POST"])
def save_service():

    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    service_id = request.form.get("service_id")
    title = request.form.get("title")
    description = request.form.get("description")
    
    # ================= IMAGE UPLOAD =================
    import os
    from werkzeug.utils import secure_filename

    image = ""

    image_file = request.files.get("image")

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)

        upload_folder = os.path.join("static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        image_file.save(os.path.join(upload_folder, filename))

        image = "static/uploads/" + filename

    cursor = mysql.connection.cursor()

    if action == "INSERT":

        cursor.execute("""
        INSERT INTO tbl_services(title, description, image)
        VALUES(%s, %s, %s)
        """, (title, description,image))

        flash("Service Added Successfully", "success")

    elif action == "UPDATE":

        if image:
            cursor.execute("""
        UPDATE tbl_services
        SET title=%s,
            description=%s,
            image=%s
        WHERE id=%s
    """, (title, description, image, service_id))
        else:
            cursor.execute("""
        UPDATE tbl_services
        SET title=%s,
            description=%s
        WHERE id=%s
    """, (title, description, service_id))

        flash("Service Updated Successfully", "success")
        

    mysql.connection.commit()
    cursor.close()
    return redirect("/admin")

@service_bp.route("/delete_service/<int:id>")
def delete_service(id):
    print("DELETE SERVICE ROUTE HIT:", id)

    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM tbl_service_features WHERE service_id=%s",
        (id,)
    )

    cursor.execute(
        "DELETE FROM tbl_service_details WHERE service_id=%s",
        (id,)
    )

    cursor.execute(
        "DELETE FROM tbl_services WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()
    cursor.close()

    flash("Service deleted successfully", "success")
    return redirect("/admin")

@service_bp.route("/delete_service_detail/<int:id>")
def delete_service_detail(id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM tbl_service_details
        WHERE id=%s
    """, (id,))

    mysql.connection.commit()
    cursor.close()

    flash("Service Detail deleted successfully", "success")

    return redirect("/admin")

@service_bp.route("/delete_feature/<int:id>")
def delete_feature(id):

    cursor = mysql.connection.cursor()

    cursor.execute("DELETE FROM tbl_service_features WHERE id=%s", (id,))

    mysql.connection.commit()
    cursor.close()

    flash("Feature deleted", "success")
    return redirect("/admin")

@service_bp.route("/edit_service/<int:id>")
def edit_service(id):

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tbl_services WHERE id=%s", (id,))
    service = cursor.fetchone()

    cursor.close()

    return render_template("admin/edit_service.html", service=service)

@service_bp.route("/update_service", methods=["POST"])
def update_service():

    service_id = request.form.get("id")
    title = request.form.get("title")
    description = request.form.get("description")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        UPDATE tbl_services
        SET title=%s, description=%s
        WHERE id=%s
    """, (title, description, service_id))

    mysql.connection.commit()
    cursor.close()

    flash("Updated successfully", "success")
    
    print(request.form)
    print(request.files)

    return redirect("/admin")