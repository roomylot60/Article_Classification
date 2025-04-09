import pandas as pd
from rouge import Rouge
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
import nltk
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

# NLTK 데이터 다운로드
def download_nltk_resources():
    required_resources = ['punkt', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    for resource in required_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"Downloading NLTK resource: {resource}")
            nltk.download(resource)

# NLTK 리소스 다운로드 실행
download_nltk_resources()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log'),
        logging.StreamHandler()
    ]
)

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
            early_stopping=True,
            no_repeat_ngram_size=3,
            temperature=0.7
        )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def calculate_bleu_score(candidate, reference):
    try:
        smoothie = SmoothingFunction().method1
        reference = [nltk.word_tokenize(reference)]
        candidate = nltk.word_tokenize(candidate)
        return sentence_bleu(reference, candidate, smoothing_function=smoothie)
    except Exception as e:
        logging.error(f"BLEU score calculation error: {str(e)}")
        return 0.0

def calculate_meteor_score(candidate, reference):
    try:
        return meteor_score([nltk.word_tokenize(reference)], nltk.word_tokenize(candidate))
    except Exception as e:
        logging.error(f"METEOR score calculation error: {str(e)}")
        return 0.0

# ✅ 모델별 평가 수행
for model_name, model_path in MODELS.items():
    logging.info(f"\n🚀 {model_name} 모델 요약 수행 중...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
        model.eval()

        summaries = []
        for text in tqdm(article_texts, desc=f"{model_name} 요약 중"):
            try:
                summaries.append(generate_summary(model, tokenizer, text))
            except Exception as e:
                logging.error(f"Error generating summary: {str(e)}")
                summaries.append("")  # 빈 요약으로 대체

        # ROUGE 점수 계산
        rouge = Rouge()
        try:
            rouge_scores = rouge.get_scores(summaries, reference_summaries, avg=True)
        except Exception as e:
            logging.error(f"ROUGE score calculation error: {str(e)}")
            rouge_scores = {"rouge-1": {"f": 0.0}, "rouge-2": {"f": 0.0}, "rouge-l": {"f": 0.0}}
        
        # BLEU 점수 계산
        bleu_scores = []
        for summary, ref in zip(summaries, reference_summaries):
            bleu_scores.append(calculate_bleu_score(summary, ref))
        avg_bleu = np.mean(bleu_scores) if bleu_scores else 0.0
        
        # METEOR 점수 계산
        meteor_scores = []
        for summary, ref in zip(summaries, reference_summaries):
            meteor_scores.append(calculate_meteor_score(summary, ref))
        avg_meteor = np.mean(meteor_scores) if meteor_scores else 0.0
        
        # 결과 저장
        all_results[model_name] = {
            "rouge": rouge_scores,
            "bleu": avg_bleu,
            "meteor": avg_meteor
        }
    except Exception as e:
        logging.error(f"Error processing model {model_name}: {str(e)}")
        continue

# ✅ 성능 비교 출력
logging.info("\n📊 요약 성능 비교 결과")
for model_name in MODELS:
    if model_name in all_results:
        logging.info(f"\n▶ {model_name} 모델")
        logging.info("ROUGE 점수:")
        for metric in ["rouge-1", "rouge-2", "rouge-l"]:
            score = all_results[model_name]["rouge"][metric]
            logging.info(f"  {metric.upper()}: P={score['p']:.3f}, R={score['r']:.3f}, F1={score['f']:.3f}")
        logging.info(f"BLEU 점수: {all_results[model_name]['bleu']:.3f}")
        logging.info(f"METEOR 점수: {all_results[model_name]['meteor']:.3f}")

# ✅ 결과 시각화
try:
    import matplotlib.pyplot as plt

    metrics = ['ROUGE-1 F1', 'ROUGE-2 F1', 'ROUGE-L F1', 'BLEU', 'METEOR']
    pretrained_scores = [
        all_results["Pretrained"]["rouge"]["rouge-1"]["f"],
        all_results["Pretrained"]["rouge"]["rouge-2"]["f"],
        all_results["Pretrained"]["rouge"]["rouge-l"]["f"],
        all_results["Pretrained"]["bleu"],
        all_results["Pretrained"]["meteor"]
    ]
    finetuned_scores = [
        all_results["Fine-tuned"]["rouge"]["rouge-1"]["f"],
        all_results["Fine-tuned"]["rouge"]["rouge-2"]["f"],
        all_results["Fine-tuned"]["rouge"]["rouge-l"]["f"],
        all_results["Fine-tuned"]["bleu"],
        all_results["Fine-tuned"]["meteor"]
    ]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, pretrained_scores, width, label='Pretrained')
    rects2 = ax.bar(x + width/2, finetuned_scores, width, label='Fine-tuned')

    ax.set_ylabel('Scores')
    ax.set_title('Model Performance Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()

    fig.tight_layout()
    plt.savefig('model_comparison.png')
    plt.close()
except Exception as e:
    logging.error(f"Error creating visualization: {str(e)}")
