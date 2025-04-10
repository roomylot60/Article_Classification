### db.py (MySQL 데이터베이스 연결)
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="qwer1234", database="article_db"
    )

def save_article(section, title, content, url, summary, sentiment, sentiment_score):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO articles (section, title, content, url, summary, sentiment, sentiment_score) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (section, title, content, url, summary, sentiment, sentiment_score))
    conn.commit()
    cursor.close()
    conn.close()

def get_articles(section=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM articles" if not section else "SELECT * FROM articles WHERE section = %s"
    cursor.execute(query, (section,) if section else ())
    articles = cursor.fetchall()
    cursor.close()
    conn.close()
    return articles
