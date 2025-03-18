import streamlit as st
import mysql.connector
import requests

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

# ✅ FastAPI 서버 URL
FASTAPI_URL = "http://127.0.0.1:9000"

# ✅ Streamlit Session State를 사용하여 탭 및 기사 ID 유지
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "뉴스 분석"
if "article_id" not in st.session_state:
    st.session_state.article_id = None
if "section" not in st.session_state:
    st.session_state.section = None

valid_tabs = ["뉴스 분석", "저장된 기사 목록", "기사 상세 보기"]

# ✅ Streamlit 사이드바 설정 (선택된 탭을 유지)
def set_tab(tab_name):
    st.session_state.selected_tab = tab_name

tabs = st.sidebar.radio(
    "페이지 선택",
    valid_tabs,
    index=valid_tabs.index(st.session_state.selected_tab),
    key="sidebar_tabs",
    on_change=set_tab,
    args=(st.session_state.selected_tab,)
)

# ✅ 탭 변경 시 URL 업데이트 (선택된 탭이 유지되도록 설정)
st.experimental_set_query_params(tab=st.session_state.selected_tab, article=st.session_state.article_id, section=st.session_state.section)

# ✅ 뉴스 분석 탭
if tabs == "뉴스 분석":
    st.session_state.selected_tab = "뉴스 분석"
    st.title("📰 네이버 뉴스 요약 및 감성 분석")
    section = st.selectbox("분석할 뉴스 섹션을 선택하세요", list(SECTION_URLS.keys()))
    n_articles = st.number_input("분석할 기사 개수", min_value=1, max_value=20, value=10, step=1)
    
    if st.button("분석 시작"):
        api_url = f"{FASTAPI_URL}/analyze_section/"
        response = requests.get(api_url, params={"section": section, "count": n_articles}, timeout=10)
        if response.status_code == 200:
            results = response.json()
            st.subheader(f"📄 {section} 섹션 뉴스 분석 결과")
            for idx, result in enumerate(results, start=1):
                article_id = result.get('id')  # ✅ 실제 기사 ID를 가져옴
                if isinstance(article_id, int):  # ✅ ID가 정수형인지 확인하여 잘못된 형식 방지
                    st.session_state.article_id = article_id
                    st.session_state.section = section
                    st.session_state.selected_tab = "기사 상세 보기"
                    detail_url = f"http://localhost:8501/?article={article_id}&section={section}&tab=기사 상세 보기"
                    st.markdown(f"### [{idx}. {result.get('제목', '제목 없음')}] [🔗 상세 보기]({detail_url})")
                    st.write(f"📃 **요약:** {result.get('요약', '요약 없음')}")
                    st.write(f"🧐 **감성 분석:** {result['감성 분석 결과'].get('감정', '분석 불가')} (확률: {result['감성 분석 결과'].get('확률', 0):.2f})")
                    if st.button(f"🔎 상세 보기 {idx}", key=f"detail_{idx}"):
                        st.session_state.selected_tab = "기사 상세 보기"
                        st.experimental_rerun()
                    st.write("---")
                else:
                    st.error("❌ 잘못된 기사 ID 형식입니다.")

# ✅ 기사 상세 보기 탭 (버튼 상태 유지)
elif tabs == "기사 상세 보기":
    st.session_state.selected_tab = "기사 상세 보기"
    st.title("📌 기사 상세 정보")
    
    if st.session_state.article_id and st.session_state.section:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM articles WHERE id=%s", (st.session_state.article_id,))
            article = cursor.fetchone()
            cursor.close()
            conn.close()
        else:
            article = None

        if article:
            st.markdown(f"🔗 [기사 원문 보기]({article['url']})", unsafe_allow_html=True)
            st.write(f"📃 **제목:** {article['title']}")
            st.write(f"📖 **본문:**\n{article['content']}")
            st.write(f"📃 **요약:** {article['summary']}")
            st.write(f"🧐 **감성 분석:** {article['sentiment']} (확률: {article['sentiment_score']:.2f})")
        else:
            st.error("❌ 해당 기사 정보를 찾을 수 없습니다.")
    else:
        st.error("🔹 기사 정보를 찾을 수 없습니다.")
