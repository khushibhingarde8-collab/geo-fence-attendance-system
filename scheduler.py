from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from flask_mail import Message

from config import mysql
from extensions import mail
from database import attendance_engine, auto_force_checkout
from pytz import timezone
ist = timezone("Asia/Kolkata")

def send_wishes():

    today = date.today()

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT
            employee_id,
            first_name,
            email,
            comp_mail,
            dob,
            doj
        FROM employees
    """)

    employees = cursor.fetchall()

    for emp in employees:

        employee_id = emp[0]  

        name = emp[1]

        email = emp[3] if emp[3] else emp[2]

        dob = emp[4]

        joining_date = emp[5]

        # Birthday
        if dob and dob.month == today.month and dob.day == today.day:

            # Check if already sent today
            cursor.execute("""
            SELECT wish_id
            FROM employee_wishes_log
            WHERE employee_id=%s
            AND wish_type='birthday'
            AND wish_date=CURDATE()
            """, (employee_id,))

            existing = cursor.fetchone()

            if existing:
                continue

            # Send email
            msg = Message(
                subject="🎂 Happy Birthday",
                recipients=[email]
            )

            msg.html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #ddd;padding:20px;">

                <div style="text-align:center;">
                    <img src="https://your-domain.com/static/logos/PCE_2.png"
                         width="180">
                </div>

                <hr>

                <h2 style="color:#0d6efd;text-align:center;">
                    🎂 Happy Birthday {name}!
                </h2>

                <p>
                    Dear {name},
                </p>

                <p>
                    Wishing you a wonderful birthday filled with happiness,
                    good health, and success.
                </p>

                <p>
                    May this year bring new opportunities and achievements
                    in both your personal and professional life.
                </p>

                <br>

                <p>
                    Thanks & Regards,<br>
                    <strong>Team PCE</strong>
                </p>

            </div>
            """

            mail.send(msg)

             # Save log AFTER sending
            cursor.execute("""
            INSERT INTO employee_wishes_log
            (
                employee_id,
                wish_type,
                wish_date
            )
            VALUES
            (%s,'birthday',CURDATE())
            """, (employee_id,))

            mysql.connection.commit()


        # Work Anniversary
        if joining_date and joining_date.month == today.month and joining_date.day == today.day:

            cursor.execute("""
            SELECT wish_id
            FROM employee_wishes_log
            WHERE employee_id=%s
            AND wish_type='anniversary'
            AND wish_date=CURDATE()
            """, (employee_id,))

            existing = cursor.fetchone()

            if existing:
                continue


            years = today.year - joining_date.year

            msg = Message(
                subject="🎉 Happy Work Anniversary",
                recipients=[email]
            )

            msg.html = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #ddd;padding:20px;">
            
                <div style="text-align:center;">
                    <img src="https://your-domain.com/static/logos/PCE_2.png"
                         width="180">
                </div>
            
                <hr>
            
                <h2 style="color:#198754;text-align:center;">
                    🎉 Happy Work Anniversary!
                </h2>
            
                <p>
                    Dear {name},
                </p>
            
                <p>
                    Congratulations on completing
                    <strong>{years} years</strong> with PCE.
                </p>
            
                <p>
                    We sincerely appreciate your dedication,
                    hard work, and contribution to our success.
                </p>
            
                <br>
            
                <p>
                    Thanks & Regards,<br>
                    <strong>Team PCE</strong>
                </p>
            
            </div>
            """

            mail.send(msg)

            cursor.execute("""
            INSERT INTO employee_wishes_log
            (
                employee_id,
                wish_type,
                wish_date
            )
            VALUES
            (%s,'anniversary',CURDATE())
            """, (employee_id,))

            mysql.connection.commit()

    cursor.close()


def start_scheduler(app):

    scheduler = BackgroundScheduler(timezone=ist)

    # Wrapper for Birthday Wishes
    def run_send_wishes():
        with app.app_context():
            send_wishes()

    # Wrapper for Attendance Engine
    def run_attendance_engine():
        with app.app_context():
            attendance_engine()

    # Wrapper for Auto Force Checkout
    def run_auto_force_checkout():
        with app.app_context():
            auto_force_checkout()

    # Birthday & Work Anniversary (9:00 AM)
    scheduler.add_job(
        run_send_wishes,
        trigger="cron",
        hour=9,
        minute=0,
        id="wish_scheduler",
        replace_existing=True
    )

    # Attendance Engine (7:00 PM)
    scheduler.add_job(
        run_attendance_engine,
        trigger="cron",
        hour=19,
        minute=0,
        id="attendance_engine",
        replace_existing=True
    )

    # Auto Force Checkout (11:00 PM)
    scheduler.add_job(
        run_auto_force_checkout,
        trigger="cron",
        hour=23,
        minute=0,
        id="auto_force_checkout",
        replace_existing=True
    )

    scheduler.start()

    return scheduler