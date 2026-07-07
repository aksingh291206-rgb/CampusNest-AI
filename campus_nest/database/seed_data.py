import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "campusnest.db")


def seed_personnel():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()


    personnel_data = [

        (
            "Raj Sharma",
            "warden",
            "9876543210"
        ),

        (
            "Amit Verma",
            "security",
            "9876543211"
        ),

        (
            "Rohit Singh",
            "maintenance",
            "9876543212"
        )

    ]


    cursor.executemany(

        """
        INSERT INTO personnel
        (name, role, phone)

        VALUES (?, ?, ?)
        """,

        personnel_data

    )


    conn.commit()

    conn.close()

    print("Personnel data inserted successfully.")



if __name__ == "__main__":
    seed_personnel()