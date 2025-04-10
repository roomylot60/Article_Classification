### pages/detail.py (기사 상세 정보 페이지)
import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:9000"

# 페이지 제목
st.title("📖 기사 상세 내용")

# URL에서 선택된 기사 ID 가져오기
selected_article_ids = st.session_state.get("selected_article_ids", [])

if selected_article_ids:
    for article_id in selected_article_ids:
        # FastAPI에서 기사 상세 정보 가져오기
        if article_id is None:
            st.error("❌ 유효하지 않은 기사 ID (None)")
            continue
        response = requests.get(f"{FASTAPI_URL}/article/{article_id}")

        if response.status_code == 200:
            article = response.json()

            st.subheader(article.get("title", "제목 없음"))
            st.write(f"🗂️ **섹션:** {article.get('section', '알 수 없음')}")
            st.write(f"📅 **작성일:** {article.get('created_at', '알 수 없음')}")
            st.markdown(f"🔗 [기사 링크]({article.get('url', '#')})")
            st.write("---")
            st.write(f"📝 **본문:**\n\n{article.get('content', '본문 없음')}")
            st.write("---")
            st.write(f"📃 **요약:** {article.get('summary', '요약 없음')}")
            st.write(f"🧐 **감성 분석:** {article.get('sentiment', '분석 없음')} (점수: {article.get('sentiment_score', 0):.2f})")
            st.write("===")

        else:
            st.error(f"❌ 기사 정보를 불러올 수 없습니다. 오류 코드: {response.status_code}")

else:
    st.warning("⚠ 기사 ID가 없습니다. 먼저 [기사 목록](?page=articles)에서 기사를 선택하세요.")

# 기사 목록으로 돌아가기
st.markdown('<a href="/articles" target="_self">🔙 기사 목록으로 돌아가기</a>', unsafe_allow_html=True)
