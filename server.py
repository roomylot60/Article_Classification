### server.py (FastAPI 백엔드 서버)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from db import get_db_connection
from news_scraper import analyze_section
from datetime import datetime, timedelta

# ✅ FastAPI 인스턴스 생성 (중복 방지)
app = FastAPI()

# ✅ CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FastAPI 서버가 실행 중입니다."}

# ✅ 통계 데이터 API
@app.get("/statistics")
def get_statistics():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 전체 기사 수
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        total_articles = cursor.fetchone()["count"]

        # 오늘 수집된 기사 수
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) as count FROM articles WHERE DATE(created_at) = %s", (today,))
        today_articles = cursor.fetchone()["count"]

        # 평균 감성 점수
        cursor.execute("SELECT AVG(sentiment_score) as avg_score FROM articles")
        avg_sentiment = cursor.fetchone()["avg_score"] or 0

        # 섹션별 기사 수
        cursor.execute("SELECT section, COUNT(*) as count FROM articles GROUP BY section")
        section_counts = {row["section"]: row["count"] for row in cursor.fetchall()}

        # 일별 기사 수 추이 (최근 7일)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count 
            FROM articles 
            WHERE DATE(created_at) >= %s 
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (seven_days_ago,))
        daily_counts = {row["date"].strftime("%Y-%m-%d"): row["count"] for row in cursor.fetchall()}

        return {
            "total_articles": total_articles,
            "today_articles": today_articles,
            "average_sentiment": avg_sentiment,
            "section_counts": section_counts,
            "daily_counts": daily_counts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connection.close()

# ✅ 뉴스 크롤링 API
@app.get("/analyze_section/")
async def analyze_news_section(section: str, count: int = 10):
    return await analyze_section(section, count)

# ✅ 데이터 모델 정의 (기사 저장 시 유효성 검사)
class Article(BaseModel):
    section: str
    title: str
    url: str
    content: str
    summary: str
    sentiment: str
    sentiment_score: float

# ✅ 기사 저장 API
@app.post("/save_article")
def save_article(article: Article):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # ✅ URL 중복 여부 확인
        cursor.execute("SELECT id FROM articles WHERE url = %s", (article.url,))
        existing = cursor.fetchone()

        if existing:
            print(f"⚠️ 이미 저장된 기사입니다: ID={existing['id']}")
            return {"message": "이미 저장된 기사입니다.", "id": existing["id"]}

        # ✅ 새로운 기사 삽입
        query = """
            INSERT INTO articles (section, title, url, content, summary, sentiment, sentiment_score, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        values = (
            article.section,
            article.title,
            article.url,
            article.content,
            article.summary,
            article.sentiment,
            article.sentiment_score
        )

        print("🟢 [DEBUG] SQL 실행:", values)
        cursor.execute(query, values)
        connection.commit()

        inserted_id = cursor.lastrowid
        print("✅ 저장 성공! ID:", inserted_id)
        return {"message": "기사 저장 완료", "id": inserted_id}

    except Exception as e:
        print("🔴 [ERROR] MySQL 저장 중 오류 발생:", str(e))
        raise HTTPException(status_code=500, detail=f"MySQL 오류: {str(e)}")

    finally:
        cursor.close()
        connection.close()

@app.get("/articles")
def get_articles():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # ✅ `section` 컬럼 추가하여 가져오기
        cursor.execute("SELECT id, section, title, summary, sentiment, sentiment_score FROM articles ORDER BY created_at DESC")
        articles = cursor.fetchall()
        return {"articles": articles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connection.close()

# ✅ 특정 기사 상세 조회 API
@app.get("/article/{article_id}")
def get_article_detail(article_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        article = cursor.fetchone()
        if article:
            print("🟢 상세 조회 성공:", article)  # ✅ 로그 추가
            return article
        else:
            raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")

    except Exception as e:
        print("🔴 DB 조회 중 오류:", str(e))  # ✅ 로그로 에러 확인
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connection.close()


# ✅ 특정 기사 삭제 API 추가
@app.delete("/delete_article/{article_id}")
def delete_article(article_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 기사 삭제 SQL 실행
        cursor.execute("DELETE FROM articles WHERE id = %s", (article_id,))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")

        return {"message": "기사 삭제 완료"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        connection.close()

# ✅ FastAPI 서버 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000, reload=True)
