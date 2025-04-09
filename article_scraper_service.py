import asyncio
import schedule
import time
import logging
import sys
import os
from datetime import datetime
from news_scraper import analyze_section
from db import save_article

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ArticleScraper:
    def __init__(self):
        self.sections = ["정치", "경제", "사회", "생활", "세계", "IT"]
        self.max_retries = 3
        self.retry_delay = 300  # 5분

    async def article_analysis(self, section):
        """특정 섹션의 기사를 크롤링하고, 요약 및 감성 분석 후 데이터베이스에 저장합니다."""
        for attempt in range(self.max_retries):
            try:
                logging.info(f"{section} 섹션의 기사를 가져오는 중... (시도 {attempt + 1}/{self.max_retries})")
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
                    logging.info(f"{section} 섹션에서 {len(articles)}개의 기사를 저장했습니다.")
                    return True
                else:
                    logging.error(f"{section} 섹션의 기사 가져오기 오류: {articles['error']}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                    continue
            except Exception as e:
                logging.error(f"{section} 섹션 처리 중 오류 발생: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                continue
        return False

    async def run_scraping(self):
        """모든 섹션에 대해 크롤링 작업을 수행합니다."""
        tasks = [self.article_analysis(section) for section in self.sections]
        results = await asyncio.gather(*tasks)
        success_rate = sum(results) / len(results)
        logging.info(f"크롤링 작업 완료. 성공률: {success_rate:.2%}")

    def job(self):
        """스케줄러에서 호출될 작업 함수"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_scraping())
        loop.close()

def main():
    scraper = ArticleScraper()
    
    # 6시간마다 작업을 스케줄링
    schedule.every(6).hours.do(scraper.job)
    
    # 시작 시 즉시 한 번 실행
    scraper.job()
    
    logging.info("스케줄러가 초기화되었습니다. 다음 작업을 기다리는 중...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
        except Exception as e:
            logging.error(f"스케줄러 실행 중 오류 발생: {str(e)}")
            time.sleep(300)  # 오류 발생 시 5분 대기 후 재시도

if __name__ == "__main__":
    main() 