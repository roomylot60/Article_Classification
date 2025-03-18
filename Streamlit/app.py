import streamlit as st
import requests

# ✅ FastAPI 서버 URL
FASTAPI_URL = "http://127.0.0.1:9000"

st.set_page_config(page_title="뉴스 크롤링 및 분석", layout="wide")

st.title("📰 네이버 뉴스 크롤링 및 분석")

# ✅ 섹션 선택
section = st.selectbox("분석할 뉴스 섹션을 선택하세요", ["정치", "경제", "사회", "생활", "세계", "IT"])
n_articles = st.number_input("분석할 기사 개수", min_value=1, max_value=20, value=10, step=1)

# ✅ 크롤링 및 분석 요청
if st.button("분석 시작"):
    api_url = f"{FASTAPI_URL}/analyze_section/"
    try:
        response = requests.get(api_url, params={"section": section, "count": n_articles}, timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            st.session_state["crawled_articles"] = results  # 🔹 크롤링된 기사 저장
            st.success("✅ 크롤링 완료! '크롤링된 기사 보기' 페이지로 이동하세요.")

        else:
            st.error(f"🚨 FastAPI 서버 오류: {response.status_code}")
            st.text(response.text)

    except requests.exceptions.ConnectionError:
        st.error("🚨 FastAPI 서버에 연결할 수 없습니다. 서버 실행 상태를 확인하세요.")
    
    except requests.exceptions.Timeout:
        st.error("⏳ FastAPI 응답 시간이 초과되었습니다.")
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 요청 중 오류 발생: {str(e)}")
