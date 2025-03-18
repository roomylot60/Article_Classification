import streamlit as st
import mysql.connector

st.title("📂 저장된 기사 목록")

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

# ✅ 섹션 선택
selected_section = st.selectbox("섹션 선택", ["정치", "경제", "사회", "생활", "세계", "IT"])

# ✅ MySQL에서 데이터 조회
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, url, summary, sentiment, sentiment_score FROM articles WHERE section=%s ORDER BY created_at DESC", (selected_section,))
    articles = cursor.fetchall()
    cursor.close()
    conn.close()
else:
    articles = []

# ✅ 현재 실행 중인 서버의 포트 확인
server_port = 8503  # Streamlit이 실행 중인 포트 (기본값 8501)

# ✅ 기사 목록 출력
if articles:
    for idx, article in enumerate(articles, start=1):
        article_id = article["id"]
        detail_url = f"http://localhost:{server_port}/detail_page?article_id={article_id}"  # ✅ 페이지 이동 URL

        with st.expander(f"{idx}. {article['title']}"):
            st.markdown(f"🔗 [기사 원문 보기]({article['url']})", unsafe_allow_html=True)
            st.write(f"📃 **요약:** {article['summary']}")
            st.write(f"🧐 **감성 분석:** {article['sentiment']} (확률: {article['sentiment_score']:.2f})")

            # ✅ 직접 URL을 제공하여 클릭 시 `detail_page.py`로 이동하도록 설정
            st.markdown(f"[🔎 상세 보기]({detail_url})", unsafe_allow_html=True)

else:
    st.write(f"'{selected_section}' 섹션에 저장된 기사가 없습니다.")
