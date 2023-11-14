import sqlite3
from sqlite3 import Error


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


if __name__ == '__main__':
    db_file = "securityDatabase.db"
    conn = None


    sql_create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );"""
    file_name = "/Users/abdursiddiqui/Desktop/Security App"
    sql_create_videos_table = """
    CREATE TABLE IF NOT EXISTS videos ( 
        id INTEGER PRIMARY KEY,
        file_name VARCHAR(150),
        date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );"""

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)

        # Create the users table
        create_table(conn, sql_create_users_table)
        print("Users table is created")

        # Create the videos table
        create_table(conn, sql_create_videos_table)
        print("Videos table is created")

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
