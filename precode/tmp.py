import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import torch
import streamlit as st

# 네이버 뉴스 크롤링 함수
def fetch_news(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 네이버 뉴스 제목 가져오기
        title_tag = soup.select_one("h2#title_area")
        if not title_tag:
            title_tag = soup.select_one("h2.media_end_headline")
        title = title_tag.text.strip() if title_tag else "제목을 찾을 수 없음"
        
        # 네이버 뉴스 본문 가져오기 (더 다양한 구조 대응)
        content_tag = soup.select_one("div#dic_area")
        if not content_tag:
            content_tag = soup.select_one("div#newsct_article")
        if not content_tag:
            content_tag = soup.select_one("div.article_body_contents")
        content = content_tag.text.strip() if content_tag else "본문을 찾을 수 없음"
        
        return title, content
    else:
        return "페이지 요청 실패", "내용 없음"

# 한국어 요약을 위한 모델 (Kobart)
summarizer = pipeline("summarization", model="digit82/kobart-summarization", device=-1)

def summarize_news(text):
    if text == "본문을 찾을 수 없음":
        return "요약할 본문을 찾을 수 없습니다."
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# 한국어 감성 분석 모델 적용 (kykim/bert-kor-base)
sentiment_analyzer = pipeline("text-classification", model="kykim/bert-kor-base", device=-1)

def analyze_sentiment(text):
    sentiment = sentiment_analyzer(text)
    label_map = {"LABEL_0": "부정", "LABEL_1": "긍정"}  # 감성 분석 결과 매핑
    sentiment_label = label_map.get(sentiment[0]['label'], "알 수 없음")
    return {"감정": sentiment_label, "확률": sentiment[0]['score']}

# Streamlit 대시보드 실행
def main():
    st.title("네이버 뉴스 요약 및 감성 분석")
    st.write("네이버 뉴스 URL을 입력하면 요약과 감성 분석을 진행합니다.")
    
    url = st.text_input("네이버 뉴스 URL 입력:")
    if st.button("분석 시작"):
        with st.spinner("뉴스 데이터를 가져오는 중..."):
            title, content = fetch_news(url)
        
        if content == "본문을 찾을 수 없음":
            st.error("뉴스 본문을 찾을 수 없습니다. URL을 확인해주세요.")
        else:
            st.subheader("📌 뉴스 제목")
            st.write(title)
            
            with st.spinner("뉴스 요약 진행 중..."):
                summary = summarize_news(content)
            st.subheader("📌 뉴스 요약")
            st.write(summary)
            
            with st.spinner("감성 분석 진행 중..."):
                sentiment = analyze_sentiment(summary)
            st.subheader("📌 감성 분석 결과")
            st.write(f"감정 분석 결과: **{sentiment['감정']}** (확률: {sentiment['확률']:.2f})")

if __name__ == "__main__":
    main()
