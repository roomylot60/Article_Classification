import pandas as pd
from rouge import Rouge
from tqdm import tqdm
import asyncio
from news_scraper import summarize_news  # 직접 작성한 요약 함수

# 데이터 로딩
df = pd.read_json("summary_labeled.jsonl", lines=True)

# 기사 원문을 하나의 문자열로 합치기
df["text"] = df["article_original"].apply(lambda sentences: " ".join(sentences))

# 요약 모델 적용 (시간이 걸림)
generated_summaries = []
for article in tqdm(df["text"], desc="📄 요약 중..."):
    summary = asyncio.run(summarize_news(article))
    generated_summaries.append(summary)

# 참조 요약 (정답)
reference_summaries = df["abstractive"].tolist()

# ROUGE 평가
rouge = Rouge()
scores = rouge.get_scores(generated_summaries, reference_summaries, avg=True)

# 결과 출력
print("📊 KoBART 요약 성능 평가 (vs 참조 요약)")
for k, v in scores.items():
    print(f"{k} - P: {v['p']:.3f}, R: {v['r']:.3f}, F1: {v['f']:.3f}")
