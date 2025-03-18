import streamlit as st
import mysql.connector
import requests

# ✅ FastAPI 서버 URL
FASTAPI_URL = "http://127.0.0.1:9000"

# ✅ MySQL 연결 함수
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="qwer1234",  # 🔹 비밀번호를 실제 설정한 것으로 변경
            database="article_db"
        )
    except mysql.connector.Error as e:
        st.error(f"🚨 MySQL 연결 오류: {e}")
        return None

# ✅ URL에서 현재 선택된 탭을 확인하여 클릭된 상태 유지
query_params = st.query_params
selected_tab = query_params.get("tab", ["뉴스 분석"])[0]  # 🔹 리스트로 반환되므로 `[0]` 사용

# ✅ 올바른 탭 리스트 정의
valid_tabs = ["뉴스 분석", "저장된 기사 목록", "기사 상세 보기"]

# ✅ `selected_tab`이 유효한 값인지 확인
if selected_tab not in valid_tabs:
    selected_tab = "뉴스 분석"

# ✅ Streamlit 사이드바 설정 (클릭된 상태 유지)
tabs = st.sidebar.radio(
    "페이지 선택",
    valid_tabs,
    index=valid_tabs.index(selected_tab)
)

# ✅ 탭 변경 시 URL 업데이트 (`st.query_params` 사용)
if tabs != selected_tab:
    st.query_params["tab"] = tabs  # 🔹 선택한 탭을 URL에 반영

# ✅ 뉴스 분석 탭 (FastAPI 호출하여 기사 분석)
if tabs == "뉴스 분석":
    st.title("📰 네이버 뉴스 요약 및 감성 분석")

    # ✅ 섹션 선택 및 기사 개수 설정
    section = st.selectbox("분석할 뉴스 섹션을 선택하세요", ["정치", "경제", "사회", "생활", "세계", "IT"])
    n_articles = st.number_input("분석할 기사 개수", min_value=1, max_value=20, value=10, step=1)

    # ✅ FastAPI 서버로 기사 분석 요청
    if st.button("분석 시작"):
        api_url = f"{FASTAPI_URL}/analyze_section/"
        try:
            response = requests.get(api_url, params={"section": section, "count": n_articles}, timeout=10)

            # ✅ FastAPI 응답이 200(정상)이면 데이터 출력
            if response.status_code == 200:
                results = response.json()

                st.subheader(f"📄 {section} 섹션 뉴스 분석 결과")
                for idx, result in enumerate(results, start=1):
                    article_id = f"{section}_{idx}"  # 임시 ID 생성
                    detail_url = f"http://localhost:8501/?article={article_id}&section={section}&tab=기사 상세 보기"
                    st.markdown(f"### [{idx}. {result.get('제목', '제목 없음')}] [🔗 상세 보기]({detail_url})")
                    st.write(f"📃 **요약:** {result.get('요약', '요약 없음')}")
                    if "감성 분석 결과" in result:
                        st.write(f"🧐 **감성 분석:** {result['감성 분석 결과'].get('감정', '분석 불가')} "
                                f"(확률: {result['감성 분석 결과'].get('확률', 0):.2f})")
                    else:
                        st.write("🧐 **감성 분석:** 결과 없음")
                    st.write("---")
            
            # ✅ 오류 발생 시 FastAPI의 응답 메시지를 출력
            else:
                st.error(f"FastAPI 서버 응답 오류: {response.status_code}")
                st.text(response.text)  # 🔹 FastAPI에서 반환한 오류 메시지를 출력

        except requests.exceptions.ConnectionError:
            st.error("🚨 FastAPI 서버에 연결할 수 없습니다. FastAPI가 실행 중인지 확인하세요.")
        
        except requests.exceptions.Timeout:
            st.error("⏳ FastAPI 서버 응답 시간이 초과되었습니다. 서버 상태를 확인하세요.")
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 요청 중 오류 발생: {str(e)}")

# ✅ 저장된 기사 목록 탭 (MySQL에서 기사 조회)
elif tabs == "저장된 기사 목록":
    st.title("📂 저장된 기사 목록")
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

    # ✅ 기사 목록 출력
    if articles:
        for idx, article in enumerate(articles, start=1):
            detail_url = f"http://localhost:8501/?article={article['id']}&section={selected_section}&tab=기사 상세 보기"
            with st.expander(f"{idx}. {article['title']}"):
                st.markdown(f"🔗 [기사 원문 보기]({article['url']})", unsafe_allow_html=True)
                st.write(f"📃 **요약:** {article['summary']}")
                st.write(f"🧐 **감성 분석:** {article['sentiment']} (확률: {article['sentiment_score']:.2f})")
                st.markdown(f"[🔎 상세 보기]({detail_url})")
    else:
        st.write(f"'{selected_section}' 섹션에 저장된 기사가 없습니다.")

# ✅ 기사 상세 보기 탭
elif tabs == "기사 상세 보기":
    st.title("📌 기사 상세 정보")

    # ✅ URL에서 현재 기사 ID와 섹션을 가져오기
    article_id = query_params.get("article", [None])[0]
    section = query_params.get("section", [None])[0]

    if article_id and section:
        # ✅ MySQL에서 해당 기사 데이터 조회
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM articles WHERE id=%s", (article_id,))
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
            st.error("해당 기사 정보를 찾을 수 없습니다.")
    else:
        st.error("🔹 기사 정보를 찾을 수 없습니다.")
