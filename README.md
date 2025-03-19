## 구성
app.py
server.py
db.py
schema.sql
pages/
  search.py
  result.py
  articles.py
  detail.py

## Flow Chart
- FastAPI, Streamlit, MySQL로 구성된 멀티 페이지 앱을 생성한다.
- `app.py`:
  - streamlit을 통해 생성된 홈페이지로 구성 및 앱에 대한 설명(네이버 기사 크롤링 및 감정 분석)을 제공한다.
- `server.py`:
  - FastAPI로 구성되어 있으며, CORS 설정을 통해 클라이언트와의 통신을 허용한다.
  - 지정한 section에 대해 기사 크롤링, 저장, 조회, 삭제에 대한 API를 제공한다.
  - 기사에 대한 요약 및 감성 분석을 실행하는 함수를 포함한다.
- `db.py`:
  - MySQL 데이터베이스에 연결하고, section별 기사를 저장, 조회, 삭제하는 함수를 제공한다.
- `schema.sql`:
  - 데이터베이스 TABLE을 생성하는 Query를 제공한다.
- `pages/search.py`:
  - 기사의 크롤링을 요청한 개수만큼(default:5) 요청하고 요청 내용에 대한 오류, 혹은 완료 메시지를 반환한다.
  - 여기서 크롤링할 기사의 개수는 직접 입력할 수 있도록 지정하여 검색 버튼 이벤트를 통해 서버에 전달한다.
- `pages/result.py`:
  - `pages/search.py`에서 검색한 결과에 대해 기사 제목과, 내용의 첫 문장을 목록으로 출력한다.
  - 해당 기사들의 항목을 체크박스를 이용해 선택할 수 있도록 지정하여 선택된 항목을 데이터베이스에 저장한다.
  - 체크박스를 사용해서 선택된 기사를 상세 내용 버튼 이벤트를 통해 `pages/detail.py` 페이지에서 해당 기사의 id를 받아 상세 내용을 출력한다.
- `pages/articles.py`:
  - 데이터베이스에 저장된 기사들을 로드하여 각 section 별로 출력하고, 각 기사 항목을 선택할 수 있도록 하여 선택 항목을 데이터베이스에서 삭제한다.
  - 체크박스를 사용해서 선택된 기사를 상세 내용 버튼 이벤트를 통해 `pages/detail.py` 페이지에서 해당 기사의 id를 받아 상세 내용을 출력한다.
- `pages/detail.py`:
  - 데이터베이스에 저장된 기사들 중 `pages/result.py`나 `pages/articles.py`에서 나타나는 기사들 중 선택된 항목에 대한 상세 내용을 출력한다.
  - result, articles 페이지에서 링크를 통해 해당 페이지로 이동할 수 있도록 한다.(해당 기능은 Streamlit의 session_state를 유지하는 기능 관련 이슈로 구현 실패)
