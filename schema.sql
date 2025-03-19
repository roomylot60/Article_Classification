-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS article_db;
USE article_db;

-- 기사 테이블 생성
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    url VARCHAR(500) UNIQUE,  -- ✅ 중복 방지를 위해 UNIQUE 설정
    content TEXT,
    summary TEXT,
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);