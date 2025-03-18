import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwer1234",
            database="article_db"
        )
        if connection.is_connected():
            print("✅ MySQL 연결 성공")
            return connection
    except Error as e:
        print(f"❌ MySQL 연결 오류: {e}")
        return None
