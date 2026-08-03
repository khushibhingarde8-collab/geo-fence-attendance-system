from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from flask_mail import Message

from config import mysql
from extensions import mail


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


def start_scheduler():

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        send_wishes,
        trigger="cron",
        hour=9,
        minute=0
    )

    scheduler.start()