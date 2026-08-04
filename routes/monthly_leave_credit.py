from config import mysql
from datetime import datetime
from flask import Blueprint

monthly_leave_credit_bp = Blueprint(
    "monthly_leave_credit_bp",
    __name__
)

def monthly_leave_credit():

    conn = mysql.connection
    cur = conn.cursor()

    month = datetime.now().month
    year = datetime.now().year

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leave_credit_log(
        id INT AUTO_INCREMENT PRIMARY KEY,
        run_month INT,
        run_year INT
    )
    """)

    cur.execute("""
        SELECT * FROM leave_credit_log
        WHERE run_month=%s AND run_year=%s
    """, (month, year))

    if cur.fetchone():
        print("Already credited this month")
        cursor.close()
        return

    cur.execute("""
        UPDATE leave_balance
        SET total_leaves = total_leaves + 1.5
    """)

    cur.execute("""
        INSERT INTO leave_credit_log(run_month, run_year)
        VALUES(%s,%s)
    """, (month, year))

    conn.commit()
    cursor.close()

    print("Monthly leave credited successfully")


if __name__ == "__main__":
    monthly_leave_credit()