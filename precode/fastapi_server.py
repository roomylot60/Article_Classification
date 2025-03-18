from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import uvicorn
import warnings
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware

warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 요청 허용 (보안 고려 시 특정 도메인만 허용 가능)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 네이버 뉴스 섹션별 URL 매핑
SECTION_URLS = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "생활": "https://news.naver.com/section/103",
    "세계": "https://news.naver.com/section/104",
    "IT": "https://news.naver.com/section/105"
}

# ✅ 기본 루트("/") 경로 추가 (서버 상태 확인)
@app.get("/")
def home():
    return {"message": "AI 뉴스 요약 및 감성 분석 API 입니다. /analyze?url={뉴스URL} 또는 /analyze_section?section={섹션}&count={기사 개수} 로 요청하세요."}

# ✅ 네이버 뉴스 크롤링 함수
def fetch_news(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "페이지 요청 실패", "내용 없음"

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.select_one("h2#title_area") or soup.select_one("h2.media_end_headline")
    title = title_tag.text.strip() if title_tag else "제목을 찾을 수 없음"

    content_tag = soup.select_one("div#dic_area") or soup.select_one("div#newsct_article") or soup.select_one("div.article_body_contents")
    content = content_tag.text.strip() if content_tag else "본문을 찾을 수 없음"

    if len(content) < 10:  # 기사 본문이 너무 짧으면 로그 기록
        print(f"[WARN] {url} - 크롤링된 기사 본문이 너무 짧습니다: {content}")

    return title, content

# ✅ 한국어 요약 모델
summarizer = pipeline("summarization", model="digit82/kobart-summarization", device=-1)

def summarize_news(text):
    if not text or text.strip() == "본문을 찾을 수 없음":
        return "요약할 본문을 찾을 수 없습니다."

    if len(text) < 30:  # 최소 30자 이상 필요
        return "기사 내용이 너무 짧아 요약할 수 없습니다."

    try:
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"요약 중 오류 발생: {str(e)}"

# ✅ 한국어 감성 분석 모델
sentiment_analyzer = pipeline("text-classification", model="snunlp/KR-FinBERT", device=-1)

def analyze_sentiment(text):
    sentiment = sentiment_analyzer(text)
    label_map = {"LABEL_0": "부정", "LABEL_1": "중립", "LABEL_2": "긍정"}
    sentiment_label = label_map.get(sentiment[0]['label'], "알 수 없음")
    return {"감정": sentiment_label, "확률": sentiment[0]['score']}

# ✅ 분석 결과를 텍스트 파일에 추가 저장
def save_to_file(url, title, summary, sentiment, section="general"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = f"{section.lower()}_articles_classification.txt"
    
    with open(file_name, "a", encoding="utf-8") as file:  # 'a' 모드로 열어 내용 추가
        file.write(f"시간: {timestamp}\n")
        file.write(f"URL: {url}\n")
        file.write(f"제목: {title}\n")
        file.write(f"요약: {summary}\n")
        file.write(f"감성 분석: {sentiment['감정']} (확률: {sentiment['확률']:.2f})\n")
        file.write("-" * 80 + "\n")

# ✅ 특정 섹션의 기사들을 자동으로 감성 분석하는 API
@app.get("/analyze_section/")
def analyze_section(section: str, count: int = 10):
    if section not in SECTION_URLS:
        return {"error": "지원하지 않는 섹션입니다."}
    
    url = SECTION_URLS[section]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"}

    articles = set()
    page = 1

    while len(articles) < count and page <= 3:
        response = requests.get(url, headers=headers, params={"page": page})
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.select("div.sa_text a"):
            if "href" in a.attrs:
                href = a["href"].replace("/comment/", "/")
                if "/cluster/" not in href and href not in articles:
                    articles.add(href)

        page += 1

    if len(articles) < count:
        print(f"[WARN] {section} 섹션: 기사 부족 (요청 {count}개, 확보 {len(articles)}개)")

    results = []
    for article_url in list(articles)[:count]:  
        title, content = fetch_news(article_url)
        if content == "본문을 찾을 수 없음":
            continue  # ✅ 본문이 없는 기사 제외

        summary = summarize_news(content)
        sentiment = analyze_sentiment(summary)
        save_to_file(article_url, title, summary, sentiment, section)

        results.append({
            "URL": article_url,  # ✅ 항상 URL 포함
            "제목": title,
            "요약": summary,
            "감성 분석 결과": sentiment
        })

    if not results:
        return {"error": "요약 및 분석 가능한 기사가 없습니다."}

    return results
