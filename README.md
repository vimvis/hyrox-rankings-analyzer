# HYROX Rankings Analyzer 🏃

**최근 10개 Hyrox 대회에서 특정 조건의 Top 10 랭킹을 모두 찾아 정리해주는 웹 앱**

## 📋 기능

- 🔍 **필터 검색**: 나이그룹, 성별, 카테고리 등의 조건으로 선수 검색
- 📊 **종합 결과**: 최근 10개 대회의 결과를 한 곳에서 비교
- 📥 **CSV 다운로드**: 결과를 CSV 파일로 내보내기
- 🖨️ **인쇄 기능**: 결과를 인쇄하기
- ⚡ **빠른 캐싱**: 동일 검색 결과는 캐시에서 빠르게 제공
- 🎨 **반응형 디자인**: 모바일, 태블릿, 데스크톱 모두 지원

## 🚀 설치 및 실행

### 1️⃣ 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2️⃣ 설치

```bash
# 저장소 클론 또는 파일 다운로드
cd hyrox-rankings-analyzer

# 가상 환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3️⃣ 실행

**개발 모드 (DEBUG ON):**
```bash
python app.py
```

**프로덕션 모드 (WSGI 서버 사용):**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 4️⃣ 접속

브라우저에서 다음 주소로 접속:
```
http://localhost:5000
```

## 📖 사용 방법

### 기본 사용법

1. **필터 조건 선택**
   - **나이 그룹**: 16-24, 25-29, 30-34, ... , 75-79 중 선택
   - **성별**: 남자(M) 또는 여자(W) 선택
   - **카테고리**:
     - `HYROX (싱글)`: 개인 참가
     - `HYROX DOUBLES`: 2명 팀
     - `HYROX ELITE`: 엘리트 레벨
     - `HYROX ELITE DOUBLES`: 엘리트 2명 팀
     - `HYROX TEAM RELAY`: 팀 릴레이
     - `HYROX ADAPTIVE`: 장애인 카테고리

2. **옵션 설정**
   - **Top N**: 각 대회별 상위 N명 (기본값: 10)
   - **최근 대회 수**: 조사할 지난 대회 수 (기본값: 10)

3. **검색 시작**
   - "🔍 검색 시작" 버튼 클릭
   - 데이터 로딩 중 (수초 소요)
   - 결과 표시

4. **결과 활용**
   - 📊 통계: 총 대회 수, 선수 수, 조건 확인
   - 📥 CSV 다운로드: 엑셀에서 분석 가능
   - 🖨️ 인쇄: 결과 출력 또는 PDF 저장

### 예시

**50-54세 남자 싱글 Top 10 검색**

1. 나이 그룹: `50-54` 선택
2. 성별: `남자` 선택
3. 카테고리: `HYROX (싱글)` 선택
4. Top N: `10` (기본값)
5. 최근 대회 수: `10` (기본값)
6. "검색 시작" 클릭

## 📁 파일 구조

```
├── app.py                  # Flask 백엔드 API
├── hyrox_scraper.py       # Hyrox 웹사이트 스크래핑 모듈
├── hyrox_app.html         # 웹 인터페이스 (프론트엔드)
├── requirements.txt        # Python 패키지 의존성
├── README.md              # 이 파일
└── .env                   # 환경 변수 (선택사항)
```

## 🔌 API 엔드포인트

### POST /api/search
랭킹 검색

**요청:**
```json
{
    "age_group": "50",
    "gender": "M",
    "division": "H",
    "top_n": 10,
    "num_races": 10
}
```

**응답:**
```json
{
    "success": true,
    "data": {
        "2025 Stockholm": [
            {
                "rank": 1,
                "firstName": "John",
                "lastName": "Doe",
                "time": "50:23:15",
                "nationality": "USA",
                "ageGroup": "50-54"
            },
            ...
        ],
        ...
    },
    "stats": {
        "total_races": 10,
        "total_participants": 100,
        "timestamp": "2024-03-18T..."
    },
    "cached": false
}
```

### GET /api/races
최근 대회 목록

**응답:**
```json
{
    "success": true,
    "races": [
        {
            "name": "2025 Stockholm",
            "date": "2025-01-18"
        },
        ...
    ]
}
```

### POST /api/cache/clear
캐시 초기화

### GET /api/stats
캐시 통계 조회

## ⚙️ 설정

### 환경 변수 (.env 파일)

```
FLASK_ENV=development
FLASK_DEBUG=True
HYROX_BASE_URL=https://results.hyrox.com
CACHE_TIMEOUT=3600
```

## 🐛 문제 해결

### 문제: "ModuleNotFoundError: No module named 'flask'"

**해결:**
```bash
pip install -r requirements.txt
```

### 문제: "Port 5000 already in use"

**해결:**
```bash
# 포트 변경
python -c "from app import app; app.run(port=8000)"

# 또는 기존 프로세스 종료 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 문제: 데이터가 로드되지 않음

- Hyrox 웹사이트가 정상 작동하는지 확인
- 인터넷 연결 확인
- 필터 조건이 올바르게 설정되었는지 확인

## 📊 성능

- **첫 검색**: 5-10초 (웹사이트에서 데이터 수집)
- **캐시된 검색**: <1초
- **동시 처리**: Flask 앱은 기본적으로 단일 스레드이므로, 프로덕션에서는 gunicorn을 사용해서 워커 수를 늘려야 함

## 🔒 보안

- CORS가 활성화되어 있습니다 (개발용)
- 프로덕션에서는 CORS 설정을 더 제한적으로 변경하세요
- API 레이트 제한 추가 권장

## 📝 라이선스

MIT License

## 🤝 기여

버그 리포트와 제안은 환영합니다.

## 📞 지원

문제가 발생하면:
1. README 내용 재확인
2. 브라우저 개발자 도구 (F12) → Console 확인
3. Flask 서버 로그 확인

## 🚀 향후 계획

- [ ] 데이터베이스 캐싱 (Redis)
- [ ] 사용자 저장 검색 기록
- [ ] 그래프 및 통계 차트
- [ ] 선수 개인 통계 페이지
- [ ] 데스크톱 앱 (Electron)
- [ ] 모바일 앱 (React Native)

---

**마지막 업데이트**: 2024-03-18
**버전**: 1.0.0
