import asyncio
import schedule
import time
import logging
import sys
import os
import psutil
from datetime import datetime
from news_scraper import analyze_section
from db import save_article, get_db_connection
from db_cleanup import update_missing_sentiment_scores, remove_duplicate_articles, check_data_integrity

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
        self.last_successful_run = None
        self.total_articles_processed = 0
        self.total_errors = 0

    def health_check(self):
        """서비스 상태 확인"""
        try:
            # 데이터베이스 연결 확인
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()

            # 메모리 사용량 확인
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # MB 단위로 변환

            # 상태 로깅
            logging.info(f"서비스 상태: 실행 중")
            logging.info(f"마지막 성공 실행: {self.last_successful_run}")
            logging.info(f"총 처리 기사 수: {self.total_articles_processed}")
            logging.info(f"총 오류 수: {self.total_errors}")
            logging.info(f"메모리 사용량: {memory_usage:.2f} MB")
            
            return True
        except Exception as e:
            logging.error(f"상태 확인 중 오류 발생: {str(e)}")
            return False

    def cleanup_database(self):
        """데이터베이스 정리 작업을 수행합니다."""
        try:
            logging.info("데이터베이스 정리 작업 시작")
            
            # 1. 중복 기사 정리
            remove_duplicate_articles()
            
            # 2. 감성 분석 점수 업데이트
            update_missing_sentiment_scores()
            
            # 3. 데이터 무결성 검사
            check_data_integrity()
            
            logging.info("데이터베이스 정리 작업 완료")
            return True
        except Exception as e:
            logging.error(f"데이터베이스 정리 중 오류 발생: {str(e)}")
            return False

    async def article_analysis(self, section):
        """특정 섹션의 기사를 크롤링하고, 요약 및 감성 분석 후 데이터베이스에 저장합니다."""
        for attempt in range(self.max_retries):
            try:
                logging.info(f"{section} 섹션의 기사를 가져오는 중... (시도 {attempt + 1}/{self.max_retries})")
                articles = await analyze_section(section)
                
                if "error" not in articles:
                    for article in articles:
                        try:
                            save_article(
                                section=section,
                                title=article["제목"],
                                content=article["본문"],
                                url=article["URL"],
                                summary=article["요약"],
                                sentiment=article["감성 분석 결과"]["감정"],
                                sentiment_score=article["감성 분석 결과"]["확률"]
                            )
                            self.total_articles_processed += 1
                            logging.info(f"기사 저장 성공: {article['제목'][:50]}... (감성 점수: {article['감성 분석 결과']['확률']:.2f})")
                        except Exception as e:
                            self.total_errors += 1
                            logging.error(f"기사 저장 중 오류 발생: {str(e)}")
                            continue
                    
                    logging.info(f"{section} 섹션에서 {len(articles)}개의 기사를 저장했습니다.")
                    self.last_successful_run = datetime.now()
                    return True
                else:
                    logging.error(f"{section} 섹션의 기사 가져오기 오류: {articles['error']}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                    continue
            except Exception as e:
                self.total_errors += 1
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
        try:
            # 상태 확인
            if not self.health_check():
                logging.error("상태 확인 실패. 서비스 재시작이 필요할 수 있습니다.")
                return

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_scraping())
            loop.close()
        except Exception as e:
            logging.error(f"작업 실행 중 오류 발생: {str(e)}")

def main():
    scraper = ArticleScraper()
    
    # 6시간마다 크롤링 작업을 스케줄링
    schedule.every(6).hours.do(scraper.job)
    
    # 1시간마다 상태 확인
    schedule.every(1).hours.do(scraper.health_check)
    
    # 12시간마다 데이터베이스 정리 작업 실행
    schedule.every(12).hours.do(scraper.cleanup_database)
    
    # 시작 시 즉시 한 번 실행
    scraper.job()
    scraper.cleanup_database()
    
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