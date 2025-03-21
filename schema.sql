CREATE DATABASE IF NOT EXISTS article_db;
USE article_db;

CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section VARCHAR(50) NOT NULL,
    title TEXT,  -- 제목 길이 제한 해제
    url VARCHAR(500) UNIQUE,  -- 중복 방지
    content LONGTEXT,  -- 기사 본문이 길 수 있음
    summary TEXT,
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
