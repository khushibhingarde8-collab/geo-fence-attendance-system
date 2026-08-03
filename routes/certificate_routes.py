from flask import Blueprint, request, render_template, session, send_file
from extensions import mail
from config import mysql
import os
from datetime import datetime
from werkzeug.utils import secure_filename

certificate_bp = Blueprint('certificate_bp', __name__)

UPLOAD_FOLDER = 'static/tds_files'

# Ensure the upload folder exists to prevent [Errno 2]
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# =========================
# 🔹 Financial Year Logic
# =========================
def get_financial_year():
    today = datetime.now()
    year = today.year

    if today.month >= 4:
        start = year
        end = year + 1
    else:
        start = year - 1
        end = year

    return f"{start}-{str(end)[-2:]}"


def get_years():
    current_year = get_financial_year()
    start_year = int(current_year[:4])

    years = []
    for i in range(3):
        y1 = start_year - i
        y2 = str(y1 + 1)[-2:]
        years.append(f"{y1}-{y2}")

    return years


# =========================
# 👤 Employee TDS View
# =========================
@certificate_bp.route('/tds', methods=['GET', 'POST'])
def tds():
    years = get_years()
    result = None

    if request.method == 'POST':
        emp_code = session.get('employee_id')
        year = request.form['year']
        quarter = request.form['quarter']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT file_name, file_path 
            FROM tds_certificates
            WHERE employee_id=%s AND financial_year=%s AND quarter=%s
        """, (emp_code, year, quarter))

        result = cursor.fetchone()

    return render_template('tds.html', years=years, result=result)


# =========================
# ⬇️ Download
# =========================
@certificate_bp.route('/download/<path:filepath>')
def download(filepath):
    return send_file(filepath, as_attachment=True)


# =========================
# 🧑‍💼 Admin Upload
# =========================
@certificate_bp.route('/upload_tds', methods=['POST'])
def upload_tds():
    emp_code = request.form['employee_code']  # updated name
    quarter = request.form['quarter']
    year = request.form['year']
    file = request.files['file']

    filename = f"{emp_code}_{year}_{quarter}.pdf"
    filename = secure_filename(filename)

    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT * FROM tds_certificates
        WHERE employee_id=%s AND financial_year=%s AND quarter=%s
    """, (emp_code, year, quarter))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE tds_certificates
            SET file_name=%s, file_path=%s
            WHERE employee_id=%s AND financial_year=%s AND quarter=%s
        """, (filename, path, emp_code, year, quarter))
    else:
        cursor.execute("""
            INSERT INTO tds_certificates
            (employee_id, quarter, financial_year, file_name, file_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (emp_code, quarter, year, filename, path))

    mysql.connection.commit()

    return "Upload Successful"