import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "campusnest.db")


def create_tables():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()


    # Personnel table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personnel (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            role TEXT NOT NULL,

            phone TEXT NOT NULL
        )
        """
    )


    # Complaints table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS complaints (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            category TEXT NOT NULL,

            description TEXT NOT NULL,

            status TEXT DEFAULT 'Pending'
        )
        """
    )


    # Leave requests table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leave_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            start_date TEXT,

            end_date TEXT,

            reason TEXT,

            status TEXT DEFAULT 'Pending'
        )
        """
    )


    conn.commit()

    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    create_tables()