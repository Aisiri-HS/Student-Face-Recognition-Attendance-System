import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",               # your MySQL username
            password="password",  # your MySQL password
            database="face_attendance" # your database name
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None
