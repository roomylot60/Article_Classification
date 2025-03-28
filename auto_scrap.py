import asyncio
import schedule
import time
from news_scraper import analyze_section
from db import save_article

async def article_analysis(section):
    """특정 섹션의 기사를 크롤링하고, 요약 및 감성 분석 후 데이터베이스에 저장합니다."""
    print(f"{section} 섹션의 기사를 가져오는 중...")
    articles = await analyze_section(section)
    if "error" not in articles:
        for article in articles:
            save_article(
                section=section,
                title=article["제목"],
                content=article["본문"],
                url=article["URL"],
                summary=article["요약"],
                sentiment=article["감성 분석 결과"]["감정"],
                sentiment_score=article["감성 분석 결과"]["확률"]
            )
        print(f"{section} 섹션에서 {len(articles)}개의 기사를 저장했습니다.")
    else:
        print(f"{section} 섹션의 기사 가져오기 오류: {articles['error']}")

def job():
    """모든 섹션에 대해 크롤링 작업을 수행합니다."""
    sections = ["정치", "경제", "사회", "생활", "세계", "IT"]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [article_analysis(section) for section in sections]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

# 6시간마다 작업을 스케줄링합니다.
schedule.every(6).hours.do(job)

print("스케줄러가 초기화되었습니다. 다음 작업을 기다리는 중...")

while True:
    schedule.run_pending()
    time.sleep(1)
    
if __name__ == "__main__":
    job()  