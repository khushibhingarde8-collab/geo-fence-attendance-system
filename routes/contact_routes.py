from flask import Blueprint, render_template
from config import mysql

contact_bp = Blueprint("contact_bp", __name__)
# =========================
# CONTACT PAGE
# =========================
@contact_bp.route("/contact")
def contact():

    cur = mysql.connection.cursor()

    # fetch social links
    cur.execute("""
        SELECT * FROM tbl_social_links
        LIMIT 1
    """)
    row = cur.fetchone()

    if row:
        social_links = {
        "facebook_link": row[1],
        "twitter_link": row[2],
        "whatsapp_link": row[3],
        "linkedin_link": row[4]
    }
    else:
        social_links = {}

    # fetch contact info
    cur.execute("""
        SELECT *
        FROM tbl_contact_info
        ORDER BY contact_id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    cur.execute("""
    SELECT
    faq_id,
    question,
    answer
    FROM tbl_faq
    ORDER BY faq_id DESC
    LIMIT 6
    """)

    faqs = cur.fetchall()
        # Fetch latest 6 FAQs
    cur.execute("""
        SELECT
            f.faq_id,
            c.category_name,
            f.question,
            f.answer
        FROM tbl_faq f
        JOIN tbl_faq_category c
        ON f.category_id = c.category_id
        ORDER BY f.faq_id ASC
        LIMIT 6
    """)

    faqs = cur.fetchall()
    cur.close()

    if row:

        contact_data = {
            "contact_id": row[0],
            "description": row[1],
            "short_address": row[2],
            "email1": row[3],
            "email2": row[4],
            "phone1": row[5],
            "phone2": row[6],
            "weekday_hours": row[7],
            "saturday_hours": row[8],
            "map_link": row[9]
        }

    else:

        contact_data = {}

    return render_template(
        "contact/contact.html",
        contact_data=contact_data,
        social_links=social_links,
        faqs=faqs
    )
    


# =========================
# FAQ PAGE
# =========================
@contact_bp.route("/FAQ")
def FAQ():

    cur = mysql.connection.cursor()

    cur.execute("""
     SELECT
     f.faq_id,
     f.category_id,
     c.category_name,
     f.question,
     f.answer
     FROM tbl_faq f
     JOIN tbl_faq_category c
     ON f.category_id = c.category_id
     ORDER BY f.faq_id DESC
     """)

    faqs = cur.fetchall()
    cur.close()

    return render_template(
        "contact/FAQ.html",
        faqs=faqs
    )









