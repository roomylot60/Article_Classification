import requests
from bs4 import BeautifulSoup

# 네이버 뉴스 섹션별 URL 매핑
SECTION_URLS = {
    "정치": "https://news.naver.com/section/100",
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "생활": "https://news.naver.com/section/103",
    "세계": "https://news.naver.com/section/104",
    "IT": "https://news.naver.com/section/105"
}

# ✅ 특정 섹션에서 기사 URL 가져오기 (num_articles 개수 정확히 유지)
def get_article_urls(section, num_articles=10):
    if section not in SECTION_URLS:
        print(f"❌ 지원하지 않는 섹션입니다: {section}")
        return []

    url = SECTION_URLS[section]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ 페이지 요청 실패: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    # ✅ 모든 기사 링크 가져오기
    article_urls = []
    for a in soup.select("div.sa_text a"):
        if "href" in a.attrs:
            href = a["href"]
            # ✅ "/cluster/"가 포함된 URL은 제외
            if "/cluster/" in href:
                continue
            # ✅ "/comment/"가 포함된 URL은 정상 기사 URL로 변환
            if "/comment/" in href:
                href = href.replace("/comment/", "/")

            article_urls.append(href)

            # ✅ 요청한 기사 개수를 충족하면 중단
            if len(article_urls) >= num_articles:
                break

    return article_urls

# ✅ 테스트 실행
if __name__ == "__main__":
    section = "정치"  # 예제: 정치 섹션 기사 10개 가져오기
    article_urls = get_article_urls(section, num_articles=10)
    
    print(f"📌 {section} 섹션 기사 URL 목록:")
    for idx, url in enumerate(article_urls, start=1):
        print(f"{idx}. {url}")
