### server.py (FastAPI 백엔드 서버)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from db import get_db_connection
from news_scraper import analyze_section

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
    cursor = connection.cursor()

    try:
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

        print("🟢 [DEBUG] SQL Query:", query)
        print("🟢 [DEBUG] Values:", values)

        cursor.execute(query, values)
        connection.commit()
        
        return {"message": "기사 저장 완료"}

    except Exception as e:
        print("🔴 [ERROR] MySQL 저장 중 오류 발생:", str(e))  # 🔹 로그 출력
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
            return article
        else:
            raise HTTPException(status_code=404, detail="해당 기사를 찾을 수 없습니다.")

    except Exception as e:
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
