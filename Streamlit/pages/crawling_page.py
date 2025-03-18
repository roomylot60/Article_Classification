import streamlit as st

st.title("📄 크롤링된 기사 목록")

# ✅ 세션 상태에서 기사 데이터 가져오기
articles = st.session_state.get("crawled_articles", [])

if articles:
    for idx, article in enumerate(articles, start=1):
        article_id = article["id"]  # ✅ 기사 ID 가져오기
        detail_url = f"/detail_page?article_id={article_id}"  # ✅ ID 포함한 URL 생성
        
        with st.expander(f"{idx}. {article['제목']}"):
            st.write(f"📃 **요약:** {article.get('요약', '요약 없음')}")
            st.write(f"🧐 **감성 분석:** {article['감성 분석 결과']['감정']} "
                    f"(확률: {article['감성 분석 결과']['확률']:.2f})")
            st.markdown(f"[🔎 상세 보기](http://localhost:8501{detail_url})")  # ✅ 상세보기 링크
else:
    st.warning("🔹 크롤링된 기사가 없습니다. '메인 페이지'에서 크롤링을 실행하세요.")
