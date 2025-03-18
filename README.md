## 🚀 프로젝트 아이디어: "AI 기반 뉴스 요약 및 감성 분석 대시보드"

### 📝 프로젝트 개요
- 네이버 뉴스 데이터를 크롤링하여 자연어 처리(NLP) 기반 뉴스 요약 및 감성 분석을 수행하고, Streamlit 대시보드를 통해 시각적으로 결과를 제공하는 프로젝트입니다.

### 1️⃣ 주요 기능 추가 및 확장 방향
|확장|요소|설명|
|---|--------|--------------------|
|1|다중 뉴스 요약|여러 개의 뉴스 기사 크롤링 및 요약 비교|
|2|감성 분석 성능 향상|더 정밀한 한국어 감성 분석 모델(snunlp/KR-FinBERT) 적용|
|3|키워드 추출 및 트렌드 분석|KoBERT + TF-IDF 적용하여 핵심 키워드 도출|
|4|뉴스 카테고리 분류|Naive Bayes, LSTM 기반 뉴스 카테고리 분류 모델 적용|
|5|모델 배포 및 API 제공|FastAPI 또는 Flask를 활용해 REST API 제공|
|6|뉴스 트렌드 분석|뉴스 감성 분석 결과를 날짜별로 시각화(Plotly 활용)|

### 2️⃣ 이력서에 기재할 수 있는 프로젝트 설명 예시

#### 📌 프로젝트명:
- 🚀 "AI 기반 뉴스 요약 및 감성 분석 대시보드"
- 📌 설명:
    - 네이버 뉴스 데이터를 크롤링하여 AI 기반 요약 및 감성 분석을 수행하고, Streamlit 대시보드를 통해 사용자가 직접 분석할 수 있도록 웹 서비스화한 프로젝트입니다.
    - 자연어 처리(NLP) 모델을 활용하여 뉴스 트렌드 파악, 감성 분석 및 카테고리 분류 기능을 추가하여 데이터 기반 뉴스 분석의 효율성을 향상하였습니다.
    - FastAPI를 활용하여 REST API를 구축하였으며, 뉴스 감성 분석 및 요약 기능을 API 형태로 제공하였습니다.
- 📌 기술 스택:
    - 데이터 수집: Requests, BeautifulSoup, Selenium, FastAPI
    - 데이터 처리 및 분석: Pandas, NumPy, Scikit-Learn
    - NLP 모델: KoBART, BERT, KR-FinBERT, KoBERT
    - 모델 배포 및 웹 대시보드: Streamlit, FastAPI, Flask
    - 데이터 시각화: Matplotlib, Seaborn, Plotly
- 📌 성과:
    - 뉴스 감성 분석 정확도를 기존 distilbert 모델 대비 +8% 향상 (KR-FinBERT 적용)
    - 사용자 입력 URL을 기반으로 실시간 뉴스 요약 및 감성 분석 기능 제공
    - FastAPI로 REST API 제공 → 다른 서비스에서도 뉴스 분석 기능 활용 가능

### 3️⃣ 프로젝트 확장을 위한 코드 예시

#### ✅ 추가된 기능
- FastAPI를 활용한 REST API 제공
- snunlp/KR-FinBERT를 사용하여 더 정밀한 감성 분석 수행
- 뉴스 키워드 추출 기능(TF-IDF + KoBERT) 추가

### 4️⃣ 이력서에서 강조할 수 있는 차별화 요소
1. 자연어 처리(NLP) 실무 활용 역량 : KoBART, KR-FinBERT 등을 활용하여 뉴스 분석 자동화 모델 개발
2. 데이터 엔지니어링 및 API 개발 경험 : 크롤링부터 데이터 전처리, API 개발(FastAPI), 배포까지 엔드투엔드(End-to-End) 프로젝트 수행 경험
3. 실시간 대시보드 개발 역량 : Streamlit을 활용하여 사용자 친화적인 데이터 분석 인터페이스 구축

### 명령어
- FastAPI: 

```bash
uvicorn server:app --host 0.0.0.0 --port 9000 --reload
# host, port를 임의 설정 가능
# fastapi backend 파일 기동

lsof -i:9000

pkill -9 12345
# 12345 : 9000포트에서 실행 중인 app의 할당 넘버

pkill -9 "python3"
# 실행중인 python3 파일들을 모두 종료
```

- Streamlit:

```bash
streamlit run main.py # stramlit frontend 파일 기동
```

---

### 1. 데이터 엔지니어링 측면에서 보완할 요소

#### 1.1 데이터 저장 및 관리 방식 개선
- 현재 뉴스 요약 및 감성 분석 결과를 로컬 텍스트 파일(`_articles_classification.txt`)에 저장하고 있는데, 데이터베이스(DB) 활용이 필요
- 개선사항:
    - PostgreSQL, MySQL 또는 MongoDB 등을 활용하여 데이터 저장
    - 저장 시 기사 URL, 제목, 원문, 요약, 감성 분석 결과, 수집 시간 등의 필드 포함
    - 데이터 정제 및 변형(Preprocessing)을 고려하여 정규화된 스키마 설계

- `MySQL` 사용:
```bash
$ mysql -u root -p < schema.sql
```

#### 1.2 데이터 파이프라인 구축
- 기사 수집, 요약, 감성 분석, 저장 과정을 자동화된 데이터 파이프라인으로 관리할 수 있도록 개선
- 개선사항:
    - Apache Airflow 같은 워크플로우 오케스트레이션 툴 도입
    - 크롤링, 전처리, 분석, 저장 등의 태스크를 주기적으로 실행하도록 스케줄링
    - 데이터 흐름이 시각적으로 관리되는 구조를 갖추면 데이터 엔지니어링 역량을 어필 가능

### 2. 모델 개선 및 추가 가능 요소

#### 2.1 더 정교한 NLP 모델 적용
- 현재 `"digit82/kobart-summarization"(KoBART)` 및 "snunlp/KR-FinBERT" 모델을 활용하고 있는데, 보다 최신의 강력한 모델을 활용
- 개선사항:
    - BERT 기반 뉴스 카테고리 분류 모델 추가
    - 네이버 뉴스 기사 제목 및 본문을 활용해 다중 분류(multi-class classification) 모델 적용
    - Hugging Face의 'koelectra-base-v3' 등의 모델 활용 가능
    - LLM(대형 언어 모델) 활용
    - Ollama를 활용하여 LLaMA3, DeepSeek-R1 같은 모델을 실험
    - 데이터셋에 따라 LLM을 활용한 요약 성능을 비교 분석

### 3. 모델 성능 평가 및 A/B 테스트
- 현재 시스템에서는 요약 및 감성 분석 결과를 제공하지만 모델 성능 평가나 A/B 테스트가 필요
- 개선사항:
    - 요약 모델의 BLEU, ROUGE 점수 측정
    - 감성 분석 모델의 정확도(Accuracy), 정밀도(Precision), 재현율(Recall), F1-score 분석
    - FastAPI에 A/B 테스트 기능 추가(예: KoBART vs. LLaMA3 요약 결과 비교 API)
    - 결과를 Streamlit 대시보드로 시각화하여 보고서 형태로 활용 가능

### 4. 배포 및 MLOps 개선
- 현재 FastAPI로 서버를 구동하지만 보다 안정적인 운영 및 확장성을 고려한 배포 환경 개선이 필요
- 개선사항:
    - Docker & Kubernetes 사용
    - FastAPI 서버를 Docker 컨테이너화하여 배포 자동화
    - Kubernetes 클러스터를 활용해 확장성 있는 MLOps 환경 구축
    - MLflow 또는 Weights & Biases(W&B) 활용
    - 모델 학습 및 배포 과정에서 버전 관리 및 성능 트래킹 추가

### 5. 추가할 수 있는 기능

#### 5.1 스트리밍 데이터 처리
- 네이버 뉴스는 지속적으로 업데이트되므로 실시간 데이터 처리를 위한 Kafka 또는 RabbitMQ 도입을 고려할 수 있습니다.
- 예시:
    - Kafka로 기사 URL을 스트리밍하고, 비동기적으로 크롤링 & 분석 수행
    - Elasticsearch + Kibana 조합을 활용해 검색 기능 강화

#### 5.2 사용자 피드백 반영
- 기사 요약 및 감성 분석 결과를 사용자에게 제공하고, **유저 피드백**을 받아 개선하는 기능을 추가할 수 있습니다.
- 예시:
    - FastAPI에 /feedback 엔드포인트 추가
    - 사용자가 제공한 피드백을 학습 데이터로 활용해 모델 Fine-tuning 진행

### 결론
- 현재 네이버 뉴스 크롤링 & 분석 시스템을 입사에 활용하려면 데이터 엔지니어링, 모델 최적화, MLOps 개선 등을 추가하여 완성도를 높일 수 있음
- 우선순위 추천:
    - DB 연동 및 자동화 파이프라인(Airflow 도입)
    - KoBERT 기반 뉴스 카테고리 분류 모델 추가
    - LLM을 활용한 요약 성능 비교 (Ollama + LLaMA3 실험)
    - Docker & Kubernetes 기반 MLOps 환경 구축
    - A/B 테스트 및 성능 평가 도구 추가