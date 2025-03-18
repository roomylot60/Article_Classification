import streamlit as st
import mysql.connector

st.set_page_config(page_title="기사 상세 보기", layout="wide")
st.title("📌 기사 상세 정보")

# ✅ MySQL 연결 함수
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwer1234",
            database="article_db"
        )
    except mysql.connector.Error as e:
        st.error(f"🚨 MySQL 연결 오류: {e}")
        return None

# ✅ URL에서 `article_id` 가져오기
query_params = st.query_params
article_id = query_params.get("article_id", [None])[0]

# ✅ URL 파라미터 확인 (디버깅용)
st.write(f"🔍 Debug: Received article_id = {article_id}")

# ✅ `article_id`가 숫자로 변환 가능한지 확인 후 변환
try:
    article_id = int(article_id)
except (TypeError, ValueError):
    st.error("🚨 Invalid article ID. Please check the URL.")
    st.stop()

# ✅ 디버깅: 변환된 `article_id` 확인
st.write(f"🔍 Debug: Converted article_id (int) = {article_id}")

# ✅ MySQL에서 해당 기사 데이터 조회
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    
    # ✅ `article_id`가 정수로 변환되었는지 확인하고 MySQL에서 조회
    query = "SELECT * FROM articles WHERE id = %s"
    cursor.execute(query, (article_id,))
    article = cursor.fetchone()
    
    cursor.close()
    conn.close()
else:
    article = None

# ✅ MySQL 조회 결과 확인 (디버깅용)
st.write(f"🔍 Debug: Query result = {article}")

# ✅ 기사 정보가 있으면 화면에 표시
if article:
    st.subheader(article['title'])  # 📰 기사 제목
    st.markdown(f"🔗 [기사 원문 보기]({article['url']})", unsafe_allow_html=True)  # 🔗 원문 링크
    st.write(f"📅 **등록 날짜:** {article['created_at']}")  # 🕒 등록 날짜
    st.write("---")  # 구분선

    # 📝 본문 및 요약
    st.subheader("📖 본문")
    st.write(article['content'])

    st.subheader("📃 요약")
    st.write(article['summary'])

    # 🧐 감성 분석 결과
    st.subheader("🧐 감성 분석 결과")
    st.write(f"**감정 분석 결과:** {article['sentiment']}")
    st.write(f"**확률:** {article['sentiment_score']:.2f}")

else:
    st.error("🚨 해당 기사 정보를 찾을 수 없습니다. MySQL에서 존재하는지 확인하세요.")
