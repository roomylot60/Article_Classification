import mysql.connector
from datetime import datetime
import logging
from news_scraper import analyze_sentiment, summarize_news

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='db_cleanup.log'
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="qwer1234", database="article_db"
    )

def update_missing_sentiment_scores():
    """감성 분석 점수가 없는 기사를 찾아 업데이트합니다."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 감성 분석 점수가 없는 기사 조회
        cursor.execute("""
            SELECT id, content, summary 
            FROM articles 
            WHERE sentiment_score IS NULL OR sentiment_score = 0
        """)
        articles = cursor.fetchall()
        
        logging.info(f"감성 분석 점수가 없는 기사 {len(articles)}개 발견")
        
        for article in articles:
            try:
                # 요약이 없는 경우 요약 생성
                if not article['summary']:
                    summary = summarize_news(article['content'])
                    cursor.execute(
                        "UPDATE articles SET summary = %s WHERE id = %s",
                        (summary, article['id'])
                    )
                else:
                    summary = article['summary']
                
                # 감성 분석 수행
                sentiment_label, sentiment_score = analyze_sentiment(summary)
                
                # 데이터베이스 업데이트
                cursor.execute("""
                    UPDATE articles 
                    SET sentiment = %s, sentiment_score = %s 
                    WHERE id = %s
                """, (sentiment_label, sentiment_score, article['id']))
                
                logging.info(f"기사 ID {article['id']} 업데이트 완료: 감성={sentiment_label}, 점수={sentiment_score}")
                
            except Exception as e:
                logging.error(f"기사 ID {article['id']} 처리 중 오류 발생: {str(e)}")
                continue
        
        conn.commit()
        logging.info("감성 분석 점수 업데이트 완료")
        
    except Exception as e:
        logging.error(f"감성 분석 점수 업데이트 중 오류 발생: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def remove_duplicate_articles():
    """중복 URL을 가진 기사를 정리합니다 (최신 기사만 유지)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 중복 URL 찾기
        cursor.execute("""
            SELECT url, COUNT(*) as count, MAX(created_at) as latest_date
            FROM articles
            GROUP BY url
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        
        logging.info(f"중복 URL {len(duplicates)}개 발견")
        
        for dup in duplicates:
            # 각 중복 URL에 대해 최신 기사만 남기고 삭제
            cursor.execute("""
                DELETE FROM articles 
                WHERE url = %s AND created_at < %s
            """, (dup['url'], dup['latest_date']))
            
            logging.info(f"URL {dup['url']}의 중복 기사 {dup['count']-1}개 삭제 완료")
        
        conn.commit()
        logging.info("중복 기사 정리 완료")
        
    except Exception as e:
        logging.error(f"중복 기사 정리 중 오류 발생: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def check_data_integrity():
    """데이터 무결성을 검사하고 필요한 수정을 수행합니다."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 필수 필드가 비어있는 기사 검사
        cursor.execute("""
            SELECT id, title, content, url, summary
            FROM articles
            WHERE title IS NULL OR content IS NULL OR url IS NULL
        """)
        invalid_articles = cursor.fetchall()
        
        if invalid_articles:
            logging.warning(f"필수 필드가 비어있는 기사 {len(invalid_articles)}개 발견")
            # 필요한 경우 여기에 추가적인 수정 로직을 구현할 수 있습니다
        
        # URL 형식 검사
        cursor.execute("""
            SELECT id, url
            FROM articles
            WHERE url NOT LIKE 'http%'
        """)
        invalid_urls = cursor.fetchall()
        
        if invalid_urls:
            logging.warning(f"잘못된 URL 형식의 기사 {len(invalid_urls)}개 발견")
            # 필요한 경우 여기에 URL 수정 로직을 구현할 수 있습니다
        
        logging.info("데이터 무결성 검사 완료")
        
    except Exception as e:
        logging.error(f"데이터 무결성 검사 중 오류 발생: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

def main():
    """모든 데이터베이스 정리 작업을 실행합니다."""
    logging.info("데이터베이스 정리 작업 시작")
    
    # 1. 중복 기사 정리
    remove_duplicate_articles()
    
    # 2. 감성 분석 점수 업데이트
    update_missing_sentiment_scores()
    
    # 3. 데이터 무결성 검사
    check_data_integrity()
    
    logging.info("데이터베이스 정리 작업 완료")

if __name__ == "__main__":
    main() 