### app.py (Streamlit 메인 앱)
import streamlit as st
import requests
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="뉴스 기사 분석 시스템",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 콘텐츠
st.title("📰 뉴스 기사 분석 시스템")

st.write("""
이 시스템은 뉴스 기사를 자동으로 수집하고 분석하는 AI 기반 플랫폼입니다.

### 주요 기능:
- 📰 다양한 섹션의 뉴스 기사 자동 수집
- 🤖 AI 기반 기사 요약 및 감성 분석
- 🔍 섹션별 필터링 및 검색 기능
- ⭐ 즐겨찾기 기능
- 📊 데이터 시각화 및 통계

### 사용 방법:
1. 왼쪽 사이드바에서 원하는 섹션을 선택하세요.
2. 기사 목록에서 관심 있는 기사를 선택하세요.
3. 상세 페이지에서 기사의 요약과 감성 분석 결과를 확인하세요.
4. 즐겨찾기 기능을 사용하여 중요한 기사를 저장하세요.
""")

# 시스템 상태 표시
st.header("📊 시스템 상태")
try:
    response = requests.get("http://127.0.0.1:9000/statistics")
    if response.status_code == 200:
        try:
            stats = response.json()
            if isinstance(stats, dict):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📚 총 기사 수", f"{stats.get('total_articles', 0):,}")
                with col2:
                    st.metric("📅 오늘 수집된 기사", f"{stats.get('today_articles', 0):,}")
                with col3:
                    st.metric("😊 평균 감성 점수", f"{stats.get('average_sentiment', 0):.2f}")
            else:
                st.error("❌ 서버 응답 형식이 올바르지 않습니다.")
        except requests.exceptions.JSONDecodeError:
            st.error("❌ 서버 응답 형식이 올바르지 않습니다.")
    elif response.status_code == 404:
        st.error("❌ 통계 엔드포인트가 존재하지 않습니다. FastAPI 서버의 엔드포인트를 확인해주세요.")
    else:
        st.error(f"❌ 서버 응답 오류: {response.status_code}")
except requests.exceptions.ConnectionError:
    st.error("❌ 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해주세요.")
