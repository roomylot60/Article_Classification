import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import asyncio

# ✅ 네이버 뉴스 섹션 URL 매핑
SECTION_URLS = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "생활": "https://news.naver.com/section/103",
    "세계": "https://news.naver.com/section/104",
    "IT": "https://news.naver.com/section/105"
}

# ✅ 기사 크롤링 (비동기)
async def fetch_news(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = await asyncio.to_thread(requests.get, url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.select_one("h2#title_area") or soup.select_one("h2.media_end_headline")
        title = title_tag.text.strip() if title_tag else "제목 없음"
        content_tag = soup.select_one("div#dic_area") or soup.select_one("div#newsct_article")
        content = content_tag.text.strip() if content_tag else "본문 없음"
        return title, content
    return "페이지 요청 실패", "본문 없음"

# ✅ 기사 요약 모델 로드
summarizer = pipeline("summarization", model="digit82/kobart-summarization", device=-1)

async def summarize_news(text):
    if not text or text == "본문 없음":
        return "요약할 본문을 찾을 수 없습니다."
    try:
        result = await asyncio.to_thread(summarizer, text, max_length=100, min_length=30, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        return f"요약 중 오류 발생: {str(e)}"

# ✅ 감성 분석 모델 로드
sentiment_analyzer = pipeline("text-classification", model="snunlp/KR-FinBERT", device=-1)

async def analyze_sentiment(text):
    sentiment = await asyncio.to_thread(sentiment_analyzer, text)
    label_map = {"LABEL_0": "부정", "LABEL_1": "중립", "LABEL_2": "긍정"}
    return label_map.get(sentiment[0]['label'], "알 수 없음"), sentiment[0]['score']

# ✅ 섹션별 뉴스 기사 크롤링 및 분석 (비동기)
async def analyze_section(section: str, count: int = 10):
    if section not in SECTION_URLS:
        return {"error": "지원하지 않는 섹션입니다."}
    
    url = SECTION_URLS[section]
    response = await asyncio.to_thread(requests.get, url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return {"error": "네이버 뉴스 섹션 페이지를 불러오지 못했습니다."}
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = set()
    for a in soup.select("div.sa_text a"):
        if "href" in a.attrs:
            href = a["href"].replace("/comment/", "/")
            if "/cluster/" not in href and href not in articles:
                articles.add(href)
        if len(articles) >= count:
            break

    results = []
    tasks = [fetch_news(article_url) for article_url in list(articles)[:count]]
    fetched_news = await asyncio.gather(*tasks)

    for article_url, (title, content) in zip(articles, fetched_news):
        if content == "본문 없음":
            continue  
        
        summary = await summarize_news(content)
        sentiment_label, sentiment_score = await analyze_sentiment(summary)

        results.append({
            "URL": article_url,
            "제목": title,
            "본문": content,
            "요약": summary,
            "감성 분석 결과": {"감정": sentiment_label, "확률": sentiment_score}
        })

    return results if results else {"error": "요약 및 분석 가능한 기사가 없습니다."}
