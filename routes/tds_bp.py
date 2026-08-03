import os
import zipfile
import shutil
import stat
import re

from flask import (
    Blueprint,
    request,
    redirect,
    flash,
    session,
    send_file
)

from werkzeug.utils import secure_filename

from config import mysql


tds_bp = Blueprint("tds_bp", __name__)


UPLOAD_FOLDER = "tds_uploads/tds"


# =========================================================
# UPLOAD ZIP
# =========================================================

@tds_bp.route("/upload_tds_zip", methods=["POST"])
def upload_tds_zip():

    if "user_id" not in session:
        return redirect("/login")

    print(request.files)

    zip_file = request.files.get("zip_file")

    print("Received:", zip_file.filename)

    if not zip_file:

        flash("❌ No ZIP file selected", "tds_mesg")
        return redirect("/admin#tdscert")

    filename = secure_filename(zip_file.filename)

    if not filename.endswith(".zip"):

        flash("❌ Please upload ZIP file", "tds_mesg")
        return redirect("/admin#tdscert")


    # =====================================================
    # READ ZIP NAME
    # Example:
    # DELK12345F_16A_Q1_20252026.zip
    # =====================================================

   

    try:

        zip_name = filename.replace(".zip", "")

        parts = zip_name.split("_")

        if len(parts) != 4:
            raise ValueError("Invalid format")

        tan_number = parts[0].upper().strip()
        form_type = parts[1].upper().strip()
        quarter = parts[2].upper().strip()
        financial_year = parts[3].strip()

        # TAN Validation
        tan_pattern = r"^[A-Z]{4}[0-9]{5}[A-Z]$"

        if not re.match(tan_pattern, tan_number):
            raise ValueError("Invalid TAN")

        # Form Validation
        # if form_type != "16A":
        #     raise ValueError("Invalid Form Type")

        # Quarter Validation
        if quarter not in ["Q1", "Q2", "Q3", "Q4"]:
            raise ValueError("Invalid Quarter")

        # Financial Year Validation
        fy_pattern = r"^\d{8}$"

        if not re.match(fy_pattern, financial_year):
            raise ValueError("Invalid Financial Year")

    except Exception:

        flash(
            "❌ Invalid ZIP name. Format should be: TAN_16A_Q1_20252026.zip",
            "tds_mesg"
        )

        return redirect("/admin#tdscert")


    # =====================================================
    # CHECK DUPLICATE ZIP
    # =====================================================

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT zip_id
        FROM tds_zip_uploads
        WHERE zip_name = %s
    """, (filename,))

    existing_zip = cursor.fetchone()

    if existing_zip:
        cursor.close()
        flash("❌ This ZIP file has already been uploaded.", "tds_mesg")
        return redirect("/admin#tdscert")

    cursor.close()

    # =====================================================
    # CREATE FOLDER
    # =====================================================

    upload_folder = os.path.join(
        UPLOAD_FOLDER,
        financial_year,
        quarter,
        zip_name
    )

    os.makedirs(upload_folder, exist_ok=True)


    # =====================================================
    # VALIDATE ZIP CONTENTS
    # =====================================================
    
    pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]"
    
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
        
            pdf_found = False
    
            for member in zip_ref.namelist():
            
                # Ignore folders inside ZIP
                if member.endswith("/"):
                    continue
                
                file_name = os.path.basename(member)
    
                # Allow only PDF files
                if not file_name.lower().endswith(".pdf"):
                
                    flash(
                        "❌ ZIP should contain only PDF files.",
                        "tds_mesg"
                    )
                    return redirect("/admin#tdscert")
    
                pdf_found = True
    
                pdf_name = os.path.splitext(file_name)[0].upper()
    
                if not re.match(pan_pattern, pdf_name):
                
                    flash(
                        f"❌ Invalid PDF name: {file_name}. PDF must start with a valid PAN number.",
                        "tds_mesg"
                    )
                    return redirect("/admin#tdscert")
    
            if not pdf_found:
            
                flash(
                    "❌ ZIP does not contain any PDF files.",
                    "tds_mesg"
                )
                return redirect("/admin#tdscert")
    
    except zipfile.BadZipFile:
    
        flash(
            "❌ Invalid or corrupted ZIP file.",
            "tds_mesg"
        )
        return redirect("/admin#tdscert")
    

    # =====================================================
    # SAVE ZIP
    # =====================================================

    zip_path = os.path.join(upload_folder, filename)

    zip_file.save(zip_path)

    cursor = mysql.connection.cursor()

    cursor.execute("""
    INSERT INTO tds_zip_uploads
    (
        zip_name,
        folder_path
    )
    VALUES
    (%s,%s)
    """, (
        filename,
        upload_folder
    ))

    mysql.connection.commit()

    # =====================================================
    # EXTRACT ZIP
    # =====================================================

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        zip_ref.extractall(upload_folder)

    print("Extracted Files:")

    for root, dirs, files in os.walk(upload_folder):
        for f in files:
            print(os.path.join(root, f))


    cursor = mysql.connection.cursor()


    # =====================================================
    # READ ALL PDF FILES
    # =====================================================

    files_added = 0

    for root, dirs, files in os.walk(upload_folder):

        for file in files:

            if not file.lower().endswith(".pdf"):
                continue

            print("================================")
            print("PDF Found:", file)

            pdf_name = os.path.splitext(file)[0]

            file_parts = pdf_name.split("_")

            pan_number = file_parts[0].strip().upper()

            print("PAN:", pan_number)

            file_path = os.path.join(root, file)

            cursor.execute("""
                SELECT employee_id
                FROM employees
                WHERE UPPER(TRIM(pan_number))=%s
            """, (pan_number,))

            emp = cursor.fetchone()

            print("Employee Result:", emp)

            if not emp:
                print("Employee Not Found")
                continue

            employee_id = emp[0]

            cursor.execute("""
                SELECT tds_id
                FROM tds_certificate
                WHERE employee_id=%s
                AND quarter=%s
                AND financial_year=%s
            """, (
                employee_id,
                quarter,
                financial_year
            ))

            existing = cursor.fetchone()

            if existing:
                print("Already Exists")
                continue

            cursor.execute("""
                INSERT INTO tds_certificate
                (
                    employee_id,
                    pan_number,
                    tan_number,
                    form_type,
                    quarter,
                    financial_year,
                    file_name,
                    file_path
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                employee_id,
                pan_number,
                tan_number,
                form_type,
                quarter,
                financial_year,
                file,
                file_path
            ))

            print("Inserted Successfully")

            files_added += 1


    mysql.connection.commit()

    cursor.close()

    flash(f"✅ {files_added} TDS Certificates Uploaded", "tds_mesg")

    return redirect("/admin#tdscert")



# @tds_bp.route("/upload_tds_zip", methods=["POST"])
# def upload_tds_zip():

#     print("1. Route started")

#     if "user_id" not in session:
#         return redirect("/login")

#     zip_file = request.files.get("zip_file")
#     print("2. File received")

#     if not zip_file:
#         return "No file"

#     filename = secure_filename(zip_file.filename)
#     print("3. Filename =", filename)

#     zip_name = filename.replace(".zip", "")
#     parts = zip_name.split("_")

#     tan_number = parts[0]
#     form_type = parts[1]
#     quarter = parts[2]
#     financial_year = parts[3]

#     upload_folder = os.path.join(
#         UPLOAD_FOLDER,
#         financial_year,
#         quarter,
#         zip_name
#     )

#     os.makedirs(upload_folder, exist_ok=True)
#     print("4. Folder created")

#     zip_path = os.path.join(upload_folder, filename)

#     print("5. Before save")
#     zip_file.save(zip_path)
#     print("6. After save")

#     cursor = mysql.connection.cursor()
#     print("7. Cursor created")

#     cursor.execute("""
#         INSERT INTO tds_zip_uploads
#         (zip_name, folder_path)
#         VALUES (%s, %s)
#     """, (filename, upload_folder))

#     print("8. Record inserted")

#     mysql.connection.commit()
#     print("9. Commit done")

#     with zipfile.ZipFile(zip_path, "r") as zip_ref:
#         zip_ref.extractall(upload_folder)

#     print("10. ZIP extracted")

#     return "Done"

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


@tds_bp.route("/delete_tds_zip/<int:zip_id>", methods=["POST"])
def delete_tds_zip(zip_id):

    cursor = mysql.connection.cursor()

    print("Deleting ZIP ID:", zip_id)

    cursor.execute("""
        SELECT folder_path
        FROM tds_zip_uploads
        WHERE zip_id=%s
    """, (zip_id,))

    record = cursor.fetchone()

    print("Record:", record)

    if record:

        folder_path = record[0]

        print("Folder:", folder_path)

        try:

            if folder_path and os.path.exists(folder_path):

                print("Folder Path:", folder_path)
                print("Exists Before:", os.path.exists(folder_path))

                # Delete complete uploaded folder
                shutil.rmtree(
                    folder_path,
                    onerror=remove_readonly
                )

                print("Exists After:", os.path.exists(folder_path))

                # Delete all TDS records belonging to this upload
                cursor.execute("""
                    DELETE FROM tds_certificate
                    WHERE file_path LIKE %s
                """, (folder_path + "%",))

                # Parent folders
                quarter_folder = os.path.dirname(folder_path)
                year_folder = os.path.dirname(quarter_folder)

                print("Quarter Folder:", quarter_folder)
                print("Year Folder:", year_folder)

                # Delete quarter folder if empty
                print("Quarter Folder Contents:")
                print(os.listdir(quarter_folder))

                if os.path.exists(quarter_folder) and not os.listdir(quarter_folder):

                    os.chmod(quarter_folder, stat.S_IWRITE)

                    shutil.rmtree(
                        quarter_folder,
                        ignore_errors=True
                    )

                    print("Quarter Folder Deleted")

                # Delete financial year folder if empty

                print("Year Folder Contents:")
                print(os.listdir(year_folder))

                if os.path.exists(year_folder) and not os.listdir(year_folder):

                    os.chmod(year_folder, stat.S_IWRITE)

                    shutil.rmtree(
                        year_folder,
                        ignore_errors=True
                    )

                    print("Year Folder Deleted")

        except Exception as e:

            print("Folder Delete Error:", e)

        # Delete upload record
        cursor.execute("""
            DELETE FROM tds_zip_uploads
            WHERE zip_id=%s
        """, (zip_id,))

        print("Rows Deleted:", cursor.rowcount)

        mysql.connection.commit()

    cursor.close()

    flash("✅ Upload deleted completely", "tds_mesg")

    return redirect("/admin#tdscert")


# =========================================================
# DOWNLOAD TDS
# =========================================================

@tds_bp.route("/download_tds/<int:tds_id>")
def download_tds(tds_id):

    print("SESSION:", dict(session))

    if "employee_id" not in session:
        return redirect("/login")

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            employee_id,
            file_path,
            file_name
        FROM tds_certificate
        WHERE tds_id=%s
    """, (tds_id,))

    tds = cursor.fetchone()

    print("TDS Record:", tds)

    cursor.close()

    if not tds:
        return "File Not Found"

    db_employee_id = tds[0]


    if db_employee_id != session["employee_id"]:
        return "Unauthorized Access"

    return send_file(
        tds[1],
        as_attachment=True,
        download_name=tds[2]
    )