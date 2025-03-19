### app.py (Streamlit 메인 앱)
import streamlit as st

st.set_page_config(page_title="네이버 뉴스 크롤링 및 감정 분석", layout="wide")

st.title("📰 네이버 뉴스 크롤링 및 감정 분석")
st.write(
    """
    이 애플리케이션은 FastAPI, Streamlit, MySQL을 사용하여 네이버 뉴스를 크롤링하고, 
    감정 분석 및 요약을 수행하는 기능을 제공합니다.
    
    ### 기능 소개
    - 특정 섹션(정치, 경제, 사회 등)의 기사를 크롤링하여 MySQL에 저장
    - 크롤링한 기사의 요약 및 감정 분석 수행
    - 사용자가 검색한 기사 목록을 확인하고 저장 및 삭제 가능
    - 선택한 기사의 상세 정보를 조회 가능
    
    왼쪽 사이드바에서 원하는 기능을 선택하세요!
    """
)
