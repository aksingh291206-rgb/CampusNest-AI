import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "campusnest.db")


def get_connection():
    """
    Creates and returns a database connection.
    """
    return sqlite3.connect(DB_NAME)


def get_contact(role):
    """
    Fetch personnel contact details based on role.

    Example:
    role = "warden"
    returns: ("Raj Sharma", "9876543210")
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name, phone
        FROM personnel
        WHERE role=?
        """,
        (role,)
    )

    result = cursor.fetchone()

    conn.close()

    return result