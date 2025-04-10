import streamlit as st
import requests
from datetime import datetime, timedelta

FASTAPI_URL = "http://127.0.0.1:9000"

# 페이지 제목
st.title("📊 통계")

try:
    # FastAPI 서버에서 통계 데이터 가져오기
    response = requests.get(f"{FASTAPI_URL}/statistics")
    if response.status_code == 200:
        try:
            stats = response.json()
            
            if not stats:
                st.warning("⛔ 통계 데이터가 없습니다.")
                st.stop()
            
            # 전체 기사 수
            st.metric("📚 전체 기사 수", stats.get('total_articles', 0))
            
            # 오늘 수집된 기사 수
            st.metric("📅 오늘 수집된 기사 수", stats.get('today_articles', 0))
            
            # 평균 감성 점수
            avg_sentiment = stats.get('average_sentiment', 0)
            st.metric("😊 평균 감성 점수", f"{avg_sentiment:.2f}")
            
            # 섹션별 기사 수
            st.subheader("📰 섹션별 기사 수")
            section_counts = stats.get('section_counts', {})
            if section_counts:
                for section, count in section_counts.items():
                    st.write(f"- {section}: {count}개")
            else:
                st.warning("⛔ 섹션별 기사 수 데이터가 없습니다.")
            
            # 일별 기사 수 추이
            st.subheader("📈 일별 기사 수 추이")
            daily_counts = stats.get('daily_counts', {})
            if daily_counts:
                dates = []
                counts = []
                for date, count in daily_counts.items():
                    dates.append(date)
                    counts.append(count)
                
                if dates and counts:
                    st.line_chart({"기사 수": counts})
                else:
                    st.warning("⛔ 일별 기사 수 데이터가 없습니다.")
            else:
                st.warning("⛔ 일별 기사 수 데이터가 없습니다.")
                
        except requests.exceptions.JSONDecodeError:
            st.error("❌ 서버 응답 형식이 올바르지 않습니다. 서버 로그를 확인해주세요.")
            st.text(f"서버 응답: {response.text[:200]}...")  # 응답의 처음 200자만 표시
            
            # 임시 데이터 표시
            st.warning("⚠ 임시 통계 데이터를 표시합니다.")
            st.metric("📚 전체 기사 수", 0)
            st.metric("📅 오늘 수집된 기사 수", 0)
            st.metric("😊 평균 감성 점수", "0.00")
            
            st.subheader("📰 섹션별 기사 수")
            st.write("- 정치: 0개")
            st.write("- 경제: 0개")
            st.write("- 사회: 0개")
            st.write("- 생활: 0개")
            st.write("- 세계: 0개")
            st.write("- IT: 0개")
            
            st.subheader("📈 일별 기사 수 추이")
            st.warning("⛔ 일별 기사 수 데이터가 없습니다.")
            
    elif response.status_code == 404:
        st.error("❌ 통계 엔드포인트가 존재하지 않습니다. FastAPI 서버의 엔드포인트를 확인해주세요.")
        
        # 임시 데이터 표시
        st.warning("⚠ 임시 통계 데이터를 표시합니다.")
        st.metric("📚 전체 기사 수", 0)
        st.metric("📅 오늘 수집된 기사 수", 0)
        st.metric("😊 평균 감성 점수", "0.00")
        
        st.subheader("📰 섹션별 기사 수")
        st.write("- 정치: 0개")
        st.write("- 경제: 0개")
        st.write("- 사회: 0개")
        st.write("- 생활: 0개")
        st.write("- 세계: 0개")
        st.write("- IT: 0개")
        
        st.subheader("📈 일별 기사 수 추이")
        st.warning("⛔ 일별 기사 수 데이터가 없습니다.")
        
    else:
        st.error(f"❌ 서버 응답 오류: {response.status_code}")
        st.text(f"서버 응답: {response.text[:200]}...")  # 응답의 처음 200자만 표시
        
except requests.exceptions.ConnectionError:
    st.error("❌ 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해주세요.")
    
    # 임시 데이터 표시
    st.warning("⚠ 임시 통계 데이터를 표시합니다.")
    st.metric("📚 전체 기사 수", 0)
    st.metric("📅 오늘 수집된 기사 수", 0)
    st.metric("😊 평균 감성 점수", "0.00")
    
    st.subheader("📰 섹션별 기사 수")
    st.write("- 정치: 0개")
    st.write("- 경제: 0개")
    st.write("- 사회: 0개")
    st.write("- 생활: 0개")
    st.write("- 세계: 0개")
    st.write("- IT: 0개")
    
    st.subheader("📈 일별 기사 수 추이")
    st.warning("⛔ 일별 기사 수 데이터가 없습니다.")
    
except requests.exceptions.JSONDecodeError:
    st.error("❌ 서버 응답 형식이 올바르지 않습니다.")
    
    # 임시 데이터 표시
    st.warning("⚠ 임시 통계 데이터를 표시합니다.")
    st.metric("📚 전체 기사 수", 0)
    st.metric("📅 오늘 수집된 기사 수", 0)
    st.metric("😊 평균 감성 점수", "0.00")
    
    st.subheader("📰 섹션별 기사 수")
    st.write("- 정치: 0개")
    st.write("- 경제: 0개")
    st.write("- 사회: 0개")
    st.write("- 생활: 0개")
    st.write("- 세계: 0개")
    st.write("- IT: 0개")
    
    st.subheader("📈 일별 기사 수 추이")
    st.warning("⛔ 일별 기사 수 데이터가 없습니다.")

# 기사 목록으로 돌아가기
st.markdown('[🔙 기사 목록으로 돌아가기](http://localhost:8501/articles)', unsafe_allow_html=True) 