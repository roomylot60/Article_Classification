### pages/articles.py (저장된 기사 목록)
import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:9000"

st.title("📂 저장된 기사 목록 (섹션별 필터링)")

# ✅ FastAPI에서 저장된 기사 목록 불러오기
response = requests.get(f"{FASTAPI_URL}/articles")
if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        st.write("⛔ 저장된 기사가 없습니다.")
    else:
        # ✅ 섹션별 필터링을 위한 드롭다운 추가
        sections = list(set(article["section"] for article in articles))
        sections.sort()
        selected_section = st.selectbox("🔍 섹션 선택", ["전체"] + sections)

        # ✅ 선택된 섹션에 맞게 기사 필터링
        filtered_articles = [article for article in articles if selected_section == "전체" or article["section"] == selected_section]

        if not filtered_articles:
            st.write(f"⛔ 선택한 섹션({selected_section})에 저장된 기사가 없습니다.")
        else:
            st.write(f"📌 **{selected_section}** 섹션의 기사 목록:")

            selected_article_ids = []  # ✅ 선택된 기사 ID 저장 리스트

            for article in filtered_articles:
                # ✅ 기사 URL 추가
                article_url = article.get("url", "#")
                st.markdown(f"🔗 [기사 링크]({article_url})", unsafe_allow_html=True)

                # ✅ 기사 선택 체크박스 추가
                if st.checkbox(f"{article['title']} (요약: {article['summary']})", key=article["id"]):
                    selected_article_ids.append(article["id"])

                st.write("---")

            # ✅ "상세 내용" 버튼 추가 (기사 선택 시만 활성화)
            if selected_article_ids:
                if st.button("📖 상세 내용 보기"):
                    st.session_state["selected_article_ids"] = selected_article_ids  # ✅ 세션에 저장
                    st.experimental_set_query_params(page="detail")  # ✅ URL 변경
                    st.rerun()

            # ✅ "선택한 기사 삭제" 버튼 추가
            if selected_article_ids:
                if st.button("🗑️ 선택한 기사 삭제"):
                    for article_id in selected_article_ids:
                        delete_response = requests.delete(f"{FASTAPI_URL}/delete_article/{article_id}")
                        if delete_response.status_code == 200:
                            st.success(f"✅ 기사 삭제 완료: ID {article_id}")
                        else:
                            st.error(f"❌ 삭제 실패: {delete_response.json().get('detail', '알 수 없는 오류')}")

                    # ✅ 삭제 후 페이지 새로고침
                    st.rerun()

else:
    st.error("❌ 기사 목록을 불러올 수 없습니다.")



