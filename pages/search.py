### pages/search.py (기사 검색 페이지)
import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:9000"

st.title("🔎 뉴스 검색")

# ✅ 섹션 및 검색 개수 입력
section = st.selectbox("검색할 뉴스 섹션을 선택하세요", ["정치", "경제", "사회", "생활", "세계", "IT"])
n_articles = st.number_input("검색할 기사 개수", min_value=1, max_value=200, value=10)

if st.button("검색 실행"):
    api_url = f"{FASTAPI_URL}/analyze_section/"
    try:
        response = requests.get(api_url, params={"section": section, "count": n_articles}, timeout=800)
        if response.status_code == 200:
            search_results = response.json()
            
            if not search_results or "error" in search_results:
                st.warning("⛔ 검색된 기사가 없습니다.")
            else:
                # ✅ 검색 결과를 세션 상태에 저장하여 result.py에서 사용 가능하도록 함
                st.session_state["search_results"] = search_results
                st.session_state["search_section"] = section
                
                # ✅ result 페이지로 이동할 수 있도록 링크 제공
                st.success("✅ 검색이 완료되었습니다! 아래에서 기사를 선택한 후 저장하세요.")
                st.markdown("[🔍 결과 페이지로 이동](http://localhost:8501/result)")
        else:
            st.error(f"🚨 FastAPI 서버 응답 오류: {response.status_code}")
            st.text(response.text)
    
    except requests.exceptions.ConnectionError:
        st.error("🚨 FastAPI 서버에 연결할 수 없습니다. FastAPI가 실행 중인지 확인하세요.")

    except requests.exceptions.Timeout:
        st.error("⏳ FastAPI 서버 응답 시간이 초과되었습니다. 서버 상태를 확인하세요.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 요청 중 오류 발생: {str(e)}")
