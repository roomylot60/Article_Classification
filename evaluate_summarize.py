import pandas as pd
from rouge import Rouge
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ 평가할 모델 경로들
MODELS = {
    "Pretrained": "digit82/kobart-summarization",
    "Fine-tuned": "kobart_summarization_model"
}

# ✅ 기사 데이터를 로딩
df = pd.read_json("summary_labeled.jsonl", lines=True)
df["text"] = df["article_original"].apply(lambda sents: " ".join(sents))
reference_summaries = df["abstractive"].tolist()
article_texts = df["text"].tolist()

# ✅ 결과 저장용 딕셔너리
all_results = {}

# ✅ 요약 및 평가 함수
def generate_summary(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024, padding="max_length")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=128,
            min_length=30,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# ✅ 모델별 평가 수행
for model_name, model_path in MODELS.items():
    print(f"\n🚀 {model_name} 모델 요약 수행 중...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
    model.eval()

    summaries = []
    for text in tqdm(article_texts, desc=f"{model_name} 요약 중"):
        summaries.append(generate_summary(model, tokenizer, text))

    rouge = Rouge()
    scores = rouge.get_scores(summaries, reference_summaries, avg=True)
    all_results[model_name] = scores

# ✅ 성능 비교 출력
print("\n📊 요약 성능 비교 결과 (ROUGE)")
for metric in ["rouge-1", "rouge-2", "rouge-l"]:
    print(f"\n▶ {metric.upper()}")
    for model_name in MODELS:
        score = all_results[model_name][metric]
        print(f"{model_name:>12}: P={score['p']:.3f}, R={score['r']:.3f}, F1={score['f']:.3f}")
