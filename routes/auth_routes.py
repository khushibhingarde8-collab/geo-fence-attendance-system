from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash
from config import mysql
from extensions import mail
from flask_mail import Message

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    print("LOGIN WORKING FILE:", __file__)
    print("LOGIN ROUTE HIT")

    # show login page
    if request.method == "GET":
        return render_template("home/login.html")
    
    print("FORM:", request.form)

    # login logic
    data = request.get_json(silent=True)

    if data:
        email = data.get("email")
        password = data.get("password")
        fcm_token = data.get("fcm_token")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        fcm_token = request.form.get("fcm_token")

    print("EMAIL:", email)
    print("PASSWORD RECEIVED:", bool(password))
    print("FCM TOKEN RECEIVED:", bool(fcm_token))
    
    cursor = mysql.connection.cursor()
    print("DB CONNECTED")

    cursor.execute("""
        SELECT u.user_id, u.password_hash, r.role_name
        FROM tbl_user u
        JOIN tbl_user_role ur ON u.user_id = ur.user_id
        JOIN tbl_role r ON ur.role_id = r.role_id
        WHERE u.email = %s AND u.is_active = TRUE
    """, (email,))

    user = cursor.fetchone()

      # 🔎 DEBUG
    print("User from DB:", user)
    print("Entered Email:", email)
    print("Entered Password:", password)

    print("===== DEBUG =====")

    if user:
        result = check_password_hash(user[1], password)
        print("Password Match =", result)
    else:
        print("User Not Found")

    print("===== END DEBUG =====")

    if user and check_password_hash(user[1], password):

        session["user_id"] = user[0]
        session["role_name"] = user[2]  # store role in session
        session["email"] = email 

        cursor.execute("""
            SELECT employee_id
            FROM employees
            WHERE email=%s OR comp_mail=%s
        """, (email, email))

        emp = cursor.fetchone()

        print("Employee query result:", emp)

        if emp:
            session["employee_id"] = emp[0]

        print("LOGIN EMAIL:", email)
        print("EMPLOYEE FOUND:", emp)
        print("SESSION:", dict(session))   


        # save login activity
        cursor.execute("""
        INSERT INTO tbl_login_activity(user_id, ip_address)
        VALUES(%s, %s)
        """, (user[0], request.remote_addr))

        mysql.connection.commit()
        cursor.close()

        # 🔀 ROLE BASED REDIRECT
        print("ROLE FROM DATABASE:", user[2])
        if user[2] == "admin":
            return redirect("/admin")
        else:
            return redirect("/employee")

    else:
        flash("Invalid email or password")
        cursor.close()


        return redirect("/login")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("home/signup.html")

    name = request.form.get("full_name")
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]

    # 🔴 duplicate check using session
    if "registered_emails" not in session:
        session["registered_emails"] = []

    if email in session["registered_emails"]:
        flash("⚠️ You have already registered!", "error")
        return redirect("/signup")

    # ✅ SEND EMAIL TO ADMIN
    msg = Message(
        subject="New Employee Signup Request",
        sender="your_admin_email@gmail.com",
        recipients=["your_admin_email@gmail.com"]
    )

    msg.body = f"""
    New Employee Signup Request

    Name: {name}
    Email: {email}
    Phone: {phone}
    Password: {password}

    Please create account manually.
    """

    mail.send(msg)

    # store in session (to block duplicate)
    session["registered_emails"].append(email)

    flash("✅ Request sent to admin!", "success")

    return redirect("/login")

# LOGOUT
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")