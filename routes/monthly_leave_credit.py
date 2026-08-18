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

    try:
        month = datetime.now().month
        year = datetime.now().year

        # Check whether leave credit has already been given this month
        cur.execute("""
            SELECT 1
            FROM leave_credit_log
            WHERE run_month = %s
            AND run_year = %s
        """, (month, year))

        if cur.fetchone():
            print("Monthly leave has already been credited.")
            return

        # Create leave_balance records for new employees
        cur.execute("""
            INSERT INTO leave_balance (
                employee_id,
                total_leaves,
                used_leaves
            )
            SELECT
                employee_id,
                0,
                0
            FROM employees
            WHERE employee_id NOT IN (
                SELECT employee_id
                FROM leave_balance
            )
        """)

        # Credit 1.5 leave to all employees
        cur.execute("""
            UPDATE leave_balance
            SET total_leaves = total_leaves + 1.5
        """)

        # Store log so it doesn't run twice in the same month
        cur.execute("""
            INSERT INTO leave_credit_log
            (run_month, run_year)
            VALUES (%s, %s)
        """, (month, year))

        conn.commit()

        print("Monthly leave credited successfully.")

    except Exception as e:
        conn.rollback()
        print("Error while crediting monthly leave:", e)

    finally:
        cur.close()


if __name__ == "__main__":
    monthly_leave_credit()