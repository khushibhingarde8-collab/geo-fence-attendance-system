import email
from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for
# from main import mail
from app import app, mail



# ======================================================
# SEND EMAIL
# ======================================================

@app.route('/send-email', methods=['POST'])
def send_email():

    try:

        # ======================================
        # GET FORM DATA
        # ======================================

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        inquiry = request.form.get('inquiry_type')
        user_message = request.form.get('message')

        # FILE
        file = request.files.get('attachment')

        # ======================================
        # CREATE MAIL
        # ======================================
        msg = Message(
            subject=f"{name} |  Website Contact Form",
            sender=(
                f"{name} - Website Inquiry",
                app.config['MAIL_USERNAME']
            ),
            recipients=['info@pceengineering.com'],
            
            cc=[email],
            reply_to=email
        )

        # ======================================
        # MAIL BODY
        # ======================================

        msg.body = f"""
Hello Team,

A new inquiry has been submitted through the website contact form.

============

CLIENT DETAILS

Name         : {name}

Email        : {email}

Phone        : {phone}

Inquiry Type : {inquiry}

============

MESSAGE

{user_message}

============

Please respond to the customer using the email below:

{email}

============

Thanks & Regards,

{name}

Website Contact Form
"""

        # ======================================
        # ATTACH FILE
        # ======================================

        if file and file.filename != "":

            msg.attach(
                file.filename,
                file.content_type,
                file.read()
            )

        # ======================================
        # SEND MAIL
        # ======================================

        mail.send(msg)

        return redirect(url_for('contact'))

    except Exception as e:
        return f"Mail Failed : {str(e)}"


# ======================================================
# TEST ROUTE
# ======================================================

@app.route('/test')
def test_mail():

    try:

        msg = Message(

            subject="Test Mail From Website",

            sender=app.config['MAIL_USERNAME'],

            recipients=[app.config['MAIL_USERNAME']]
        )

        msg.body = """
This is a test email from Flask Mail.

Website mail system is working properly.
"""

        mail.send(msg)

        return redirect(url_for('contact'))

    except Exception as e:

        return f"Mail Failed : {str(e)}"


