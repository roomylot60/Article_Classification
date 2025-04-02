from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
import pandas as pd

# ✅ JSONL 파일을 로컬에서 pandas로 로드
df = pd.read_json("summary_labeled.jsonl", lines=True)

# ✅ train/test로 분할
train_df, eval_df = train_test_split(df, test_size=0.2, random_state=42)

# ✅ HuggingFace Dataset 형식으로 변환
from datasets import Dataset
train_dataset = Dataset.from_pandas(train_df)
eval_dataset = Dataset.from_pandas(eval_df)

# ✅ KoBART 토크나이저 및 모델 로드
model_name = "digit82/kobart-summarization"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# ✅ 전처리 함수
def preprocess_function(examples):
    inputs = [" ".join(article) for article in examples["article_original"]]
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True, padding="max_length")

    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["abstractive"], max_length=128, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# ✅ 토크나이징 적용
tokenized_train = train_dataset.map(preprocess_function, batched=True)
tokenized_eval = eval_dataset.map(preprocess_function, batched=True)

# ✅ 학습 설정
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",  # 최근 버전에서는 `eval_strategy` 사용
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=2,
    fp16=False,  # CPU 환경에서는 False로 설정
    logging_dir="./logs",
    logging_steps=10
)

# ✅ Trainer 구성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    tokenizer=tokenizer,
)

# ✅ 학습 실행
trainer.train()

# ✅ 모델 저장
model.save_pretrained("kobart_summarization_model")
tokenizer.save_pretrained("kobart_summarization_model")
