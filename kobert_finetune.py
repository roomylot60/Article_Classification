from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from datasets import Dataset
import optuna
from transformers import get_linear_schedule_with_warmup
import torch
from torch.utils.data import DataLoader
import random
import os

# CUDA 메모리 최적화 설정
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
torch.cuda.empty_cache()

# ✅ JSONL 파일을 로컬에서 pandas로 로드
df = pd.read_json("summary_labeled.jsonl", lines=True)

# ✅ 데이터 전처리 및 증강 함수
def preprocess_text(text):
    if isinstance(text, list):
        text = ' '.join(text)
    # 문장 단위로 분리
    sentences = text.split('.')
    # 빈 문장 제거
    sentences = [s.strip() for s in sentences if s.strip()]
    # 문장 순서 섞기 (데이터 증강)
    if len(sentences) > 1:
        random.shuffle(sentences)
    return '. '.join(sentences)

# ✅ 데이터 전처리 적용
df['article_original'] = df['article_original'].apply(preprocess_text)
df['abstractive'] = df['abstractive'].apply(preprocess_text)

# ✅ train/test로 분할
train_df, eval_df = train_test_split(df, test_size=0.2, random_state=42)

# ✅ HuggingFace Dataset 형식으로 변환
train_dataset = Dataset.from_pandas(train_df)
eval_dataset = Dataset.from_pandas(eval_df)

# ✅ KoBART 토크나이저 및 모델 로드
model_name = "digit82/kobart-summarization"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# ✅ 전처리 함수 개선
def preprocess_function(examples):
    # 입력 텍스트 전처리
    inputs = examples["article_original"]
    model_inputs = tokenizer(
        inputs,
        max_length=512,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )

    # 타겟 텍스트 전처리
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            examples["abstractive"],
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# ✅ 토크나이징 적용
tokenized_train = train_dataset.map(
    preprocess_function,
    batched=True,
    batch_size=8,
    remove_columns=train_dataset.column_names
)
tokenized_eval = eval_dataset.map(
    preprocess_function,
    batched=True,
    batch_size=8,
    remove_columns=eval_dataset.column_names
)

# ✅ Optuna를 사용한 하이퍼파라미터 최적화
def objective(trial):
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
    batch_size = trial.suggest_categorical("batch_size", [2, 4, 8])
    num_epochs = trial.suggest_int("num_epochs", 2, 3)
    weight_decay = trial.suggest_float("weight_decay", 0.01, 0.1)
    
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=num_epochs,
        weight_decay=weight_decay,
        save_total_limit=2,
        fp16=torch.cuda.is_available(),
        logging_dir="./logs",
        logging_steps=10,
        warmup_ratio=0.1,
        gradient_accumulation_steps=4,
        lr_scheduler_type="linear",
        optim="adamw_torch",
        max_grad_norm=1.0,
        dataloader_num_workers=0,
        remove_unused_columns=True,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        tokenizer=tokenizer,
    )

    try:
        trainer.train()
        eval_results = trainer.evaluate()
        return eval_results["eval_loss"]
    except RuntimeError as e:
        if "out of memory" in str(e):
            torch.cuda.empty_cache()
            return float('inf')
        raise e

# ✅ Optuna 최적화 실행
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=5)

# ✅ 최적의 하이퍼파라미터로 최종 학습
best_params = study.best_params
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=best_params["learning_rate"],
    per_device_train_batch_size=best_params["batch_size"],
    per_device_eval_batch_size=best_params["batch_size"],
    num_train_epochs=best_params["num_epochs"],
    weight_decay=best_params["weight_decay"],
    save_total_limit=2,
    fp16=torch.cuda.is_available(),
    logging_dir="./logs",
    logging_steps=10,
    warmup_ratio=0.1,
    gradient_accumulation_steps=4,
    lr_scheduler_type="linear",
    optim="adamw_torch",
    max_grad_norm=1.0,
    dataloader_num_workers=0,
    remove_unused_columns=True,
    report_to="none"
)

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
