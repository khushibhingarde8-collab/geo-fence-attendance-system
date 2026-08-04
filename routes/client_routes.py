import re
from flask import Blueprint, request, redirect, flash, session
from config import mysql
from flask import render_template

client_bp = Blueprint("client_bp", __name__)

# @client_bp.route("/client")
# def client_page():
#     return render_template("client/client.html")

@client_bp.route("/save_client", methods=["POST"])
def save_client():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    action = request.form.get("action")

    client_id = request.form.get("client_id")

    name = request.form.get("client_name")
    code = request.form.get("client_code")

    email = request.form.get("email") or ""

    phone = request.form.get("phone") or ""

    city = request.form.get("city")

    state = request.form.get("state")

    country = request.form.get("country")

    postal_code = request.form.get("postal_code") or ""

    gst_number = request.form.get("gst_number") or ""

    pan_number = request.form.get("pan_number") or ""



    # =========================
    # ✅ CLIENT NAME VALIDATION
    # =========================

    if len(name) > 50:

        flash("❌ Client Name too long", "client_msg")

        return redirect("/admin#clients")


    # repeated character validation
    if name.lower() == name[0].lower() * len(name):

        flash("❌ Invalid Client Name", "client_msg")

        return redirect("/admin#clients")


    # alphabets only validation
    if not re.match(r'^[A-Za-z ]+$', name):

        flash("❌ Client Name should contain only alphabets", "client_msg")

        return redirect("/admin#clients")



    # =========================
    # ✅ CLIENT CODE VALIDATION
    # =========================

    if len(code) > 15:

        flash("❌ Client Code too long", "client_msg")

        return redirect("/admin#clients")



    # =========================
    # ✅ EMAIL VALIDATION
    # =========================

    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):

        flash("❌ Invalid Email", "client_msg")

        return redirect("/admin#clients")



    # =========================
    # ✅ PHONE VALIDATION
    # =========================

    if not re.match(r'^[0-9]{10}$', phone):

        flash("❌ Invalid Phone Number", "client_msg")

        return redirect("/admin#clients")



    # =========================
    # ✅ CITY VALIDATION
    # =========================

    if len(city) > 30:

        flash("❌ City name too long", "client_msg")

        return redirect("/admin#clients")



    # =========================
    # ✅ GST VALIDATION
    # =========================

    if gst_number:

        gst_number = gst_number.upper()

        if not re.match(
            r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}$',
            gst_number
        ):

            flash("❌ Invalid GST Number", "client_msg")

            return redirect("/admin#clients")



    # =========================
    # ✅ PAN VALIDATION
    # =========================

    if pan_number:

        pan_number = pan_number.upper()

        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):

            flash("❌ Invalid PAN Number", "client_msg")

            return redirect("/admin#clients")



    cursor = mysql.connection.cursor()



    # =========================
    # 🔎 DUPLICATE CHECK
    # =========================

    if action == "INSERT":

        cursor.execute(
            """
            SELECT client_id
            FROM tbl_client
            WHERE client_name=%s
            """,
            (name,)
        )

        existing = cursor.fetchone()

        if existing:

            flash("❌ Client Name already exists!", "client_msg")

            cursor.close()

            return redirect("/admin#clients")



    elif action == "UPDATE":

        cursor.execute(
            """
            SELECT client_id
            FROM tbl_client
            WHERE client_name=%s
            AND client_id != %s
            AND is_active=TRUE
            """,
            (name, client_id)
        )

        existing = cursor.fetchone()

        if existing:

            flash("❌ Client Name already exists!", "client_msg")

            cursor.close()

            return redirect("/admin#clients")



    # =========================
    # ✅ INSERT
    # =========================

    if action == "INSERT":

        cursor.execute("""

            INSERT INTO tbl_client
            (
                client_name,
                client_code,
                email,
                phone,
                city,
                state,
                country,
                postal_code,
                gst_number,
                pan_number
            )

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        """, (

            name,
            code,
            email,
            phone,
            city,
            state,
            country,
            postal_code,
            gst_number,
            pan_number

        ))

        flash("✅ Client Added Successfully!", "client_msg")



    # =========================
    # ✅ UPDATE
    # =========================

    elif action == "UPDATE":

        cursor.execute("""

            UPDATE tbl_client

            SET
                client_name=%s,
                client_code=%s,
                email=%s,
                phone=%s,
                city=%s,
                state=%s,
                country=%s,
                postal_code=%s,
                gst_number=%s,
                pan_number=%s

            WHERE client_id=%s

        """, (

            name,
            code,
            email,
            phone,
            city,
            state,
            country,
            postal_code,
            gst_number,
            pan_number,
            client_id

        ))

        flash("✅ Client Updated Successfully!", "client_msg")



    # =========================
    # ✅ DELETE
    # =========================

    elif action == "DELETE":

        cursor.execute(
            """
            UPDATE tbl_client
            SET is_active = FALSE
            WHERE client_id=%s
            """,
            (client_id,)
        )

        flash("✅ Client Deleted Successfully!", "client_msg")



    mysql.connection.commit()

    cursor.close()

    return redirect("/admin#clients")



@client_bp.route("/check_client", methods=["POST"])
def check_client():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    name = request.form.get("client_name")

    client_id = request.form.get("client_id")

    cursor = mysql.connection.cursor()

    result = {"name_exists": False}



    if name:

        if client_id:

            cursor.execute(
                """
                SELECT client_id
                FROM tbl_client
                WHERE client_name=%s
                AND client_id!=%s
                """,
                (name, client_id)
            )

        else:

            cursor.execute(
                """
                SELECT client_id
                FROM tbl_client
                WHERE client_name=%s
                """,
                (name,)
            )

        if cursor.fetchone():

            result["name_exists"] = True



    cursor.close()

    return result



@client_bp.route("/get_client_by_code", methods=["POST"])
def get_client_by_code():

    # 🔐 LOGIN PROTECTION
    if "user_id" not in session:
        return redirect("/login")

    client_code = request.form.get("client_code")

    cursor = mysql.connection.cursor()

    cursor.execute("""

        SELECT
            client_id,
            client_name,
            email,
            phone,
            city,
            state,
            country,
            postal_code,
            gst_number,
            pan_number

        FROM tbl_client

        WHERE client_code=%s

    """, (client_code,))

    client = cursor.fetchone()

    cursor.close()



    if client:

        return {

            "exists": True,

            "client_id": client[0],

            "client_name": client[1],

            "email": client[2],

            "phone": client[3],

            "city": client[4],

            "state": client[5],

            "country": client[6],

            "postal_code": client[7],

            "gst_number": client[8],

            "pan_number": client[9]

        }

    else:

        return {"exists": False}