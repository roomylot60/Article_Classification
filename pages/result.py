### pages/result.py (검색 결과 페이지)
import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:9000"

st.title("📑 검색 결과")

# ✅ `search.py`에서 저장한 검색 결과 가져오기
search_results = st.session_state.get("search_results", [])
search_section = st.session_state.get("search_section", "알 수 없음")

if search_results:
    st.subheader(f"📄 {search_section} 섹션 뉴스 검색 결과")
    
    selected_article_ids = []  # ✅ 선택된 기사 ID 저장 리스트
    left_col, middle_col, right_col = st.columns([2, 1, 2])  # 비율 조절 가능
    with left_col:
        # ✅ 전체 선택 체크박스 추가
        select_all = st.checkbox("📌 모든 기사 선택/해제", key="select_all_result")

    for idx, result in enumerate(search_results, start=1):
        article_id = f"{search_section}_{idx}"  # 임시 ID 생성

        # ✅ 전체 선택 상태에 따라 자동 체크
        checked = select_all or st.checkbox(
            f"{idx}. {result.get('제목', '제목 없음')}",
            key=article_id
        )

        if checked:
            selected_article_ids.append(idx)  # ✅ ID 저장

        # ✅ 기사 URL 추가
        article_url = result.get("URL", "#")
        st.markdown(f"🔗 [기사 링크]({article_url})", unsafe_allow_html=True)
        st.write(f"📅 **작성일:** {result.get('작성일', '알 수 없음')}")
        st.write(f"📃 **요약:** {result.get('요약', '요약 없음')}")
        st.write("---")

    with right_col:
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            # ✅ "상세 내용" 버튼 추가 (기사 선택 시만 활성화)
            if selected_article_ids:
                if st.button("📖 상세 내용 보기"):
                    st.session_state["selected_article_ids"] = selected_article_ids  # ✅ 세션에 저장
                    st.query_params.update({"page": "detail"})  # ✅ st.experimental_set_query_params는 2024-04-11 이후 제거 변경
                    st.rerun()
        with btn_col2:
            # ✅ 기사 저장 기능 유지
            if selected_article_ids:
                if st.button("📝 선택한 기사 저장"):
                    stored_ids = []
                    for article_id in selected_article_ids:
                        # `search_results`에서 선택된 ID에 해당하는 기사를 찾아 저장
                        article = search_results[article_id - 1]
                        save_data = {
                            "section": search_section,
                            "title": article["제목"],
                            "url": article["URL"],
                            "content": article["본문"],
                            "summary": article["요약"],
                            "sentiment": article["감성 분석 결과"]["감정"],
                            "sentiment_score": article["감성 분석 결과"]["확률"]
                        }
                        response = requests.post(f"{FASTAPI_URL}/save_article", json=save_data)
                        
                        if response.status_code == 200 and "id" in response.json():
                            saved_id = response.json()["id"]
                            stored_ids.append(saved_id)
                            st.success(f"✅ 기사 저장 완료: {article['제목']}  (ID: {saved_id})")
                        else:
                            st.error(f"❌ 저장 실패: {article['제목']}")
                    # 저장한 기사 ID들을 세션에 저장하여 detail.py에서 사용 가능하도록
                    if stored_ids:
                        st.session_state["selected_article_ids"] = stored_ids
                        st.success(f"📝 총 {len(stored_ids)}개의 기사가 저장되었습니다.")
            else:
                st.warning("⚠ 저장할 기사를 선택하세요.")

else:
    st.warning("⛔ 검색된 기사가 없습니다. 먼저 [🔎 검색 페이지](http://localhost:8503/search)에서 검색을 진행하세요.")

