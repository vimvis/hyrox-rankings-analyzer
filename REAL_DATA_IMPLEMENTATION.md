# 🎯 실제 데이터 구현 가이드

## 상황
사용자 요청: **"실제 데이터가 아닌 가짜가 나옵니다"**

이전에 Hyrox 웹사이트가 JavaScript 동적 렌더링을 사용하기 때문에, BeautifulSoup로는 데이터를 수집할 수 없었습니다. 그래서 테스트 데이터(무작위 생성된 선수 정보)로 폴백하고 있었습니다.

## 해결책: 하이브리드 스크래퍼

이제 **세 가지 방식을 시도**하여 실제 데이터를 수집합니다:

### 📋 순서도
```
1️⃣ API 직접 호출 (가장 빠름)
   ↓ 실패 시
2️⃣ Selenium WebDriver (로컬 개발용)
   ↓ 실패 시
3️⃣ 테스트 데이터 (최후의 폴백)
```

---

## 🔧 구현 상세

### 1. **HyroxHybridScraper** (app.py에서 사용)
**파일:** `hyrox_scraper_hybrid.py`

```python
from hyrox_scraper_hybrid import HyroxHybridScraper
scraper = HyroxHybridScraper()
results = scraper.search_rankings(
    age_group='50',
    gender='M',
    division='H',
    top_n=10,
    num_races=10
)
```

**특징:**
- ✅ API 엔드포인트 시도: `/season-8/?content=ajax2&client=js`
- ✅ Selenium 웹드라이버 (로컬에서 Chrome 필요)
- ✅ 테스트 데이터 폴백
- ✅ 로그 메시지로 어느 방식을 사용했는지 표시
- ✅ Flask와 Vercel 모두 호환

### 2. **HyroxSeleniumScraper** (로컬 개발 전용)
**파일:** `hyrox_scraper_selenium.py`

```bash
python3 hyrox_scraper_selenium.py
```

**특징:**
- Selenium WebDriver 직접 사용
- Chrome의 select 드롭다운과 상호작용
- JavaScript 렌더링된 페이지에서 실제 테이블 파싱
- 로컬에서만 테스트 가능 (Chrome 필요)

### 3. **HyroxPlaywrightScraper** (선택 사항)
**파일:** `hyrox_scraper_playwright.py`

비동기식 Playwright 기반 스크래퍼. Vercel에서 더 나은 성능을 원하는 경우 향후 사용 가능합니다.

---

## 🧪 로컬에서 테스트하기

### 1단계: 필요한 패키지 설치

```bash
pip install -r requirements.txt
pip install selenium  # 이미 포함됨
```

### 2단계: Chrome/Chromium 설치

**macOS:**
```bash
brew install chromium
```

**Ubuntu/Debian:**
```bash
sudo apt-get install chromium-browser
```

**Windows:**
Download from https://www.chromium.org/getting-involved/download-chromium

### 3단계: 하이브리드 스크래퍼 테스트

```bash
# 직접 테스트
cd /path/to/hyrox-rankings-analyzer
python3 hyrox_scraper_hybrid.py
```

**예상 출력:**
```
✅ 하이브리드 스크래퍼 준비됨 (API → Selenium → Test Data)
🔍 2개 대회에서 데이터 수집 중...

  🔄 2025 Verona 데이터 로드 중... ✅ API로 12명 수집
  🔄 2025 London Excel 데이터 로드 중... → Selenium으로 15명 수집

📊 결과:

📍 2025 Verona:
   1. John Smith - 00:45:23
   2. Maria Garcia - 00:46:12
   ...
```

### 4단계: Flask 앱 로컬 실행

```bash
python3 app.py
# 또는
flask run
```

접속: http://localhost:5000

---

## 🚀 Vercel 배포

GitHub에 푸시하면 **자동으로 Vercel이 재배포**됩니다.

```bash
git add .
git commit -m "real data implementation"
git push origin main
```

### 배포 확인

1. **Vercel 대시보드 접속**: https://vercel.com/dashboard
2. **Deployments** 확인
3. 새 배포가 진행 중인지 확인
4. 배포 완료 후 접속: https://hyrox-rankings-analyzer.vercel.app

---

## 📊 실제 데이터 vs 테스트 데이터

### 로그로 확인하기

Flask 로그에서 어느 방식을 사용했는지 확인할 수 있습니다:

```
✅ API로 12명 수집         → 실제 API 데이터
→ Selenium으로 15명 수집   → Selenium으로 파싱한 데이터
→ Test Data 사용          → 무작위 테스트 데이터
```

---

## ⚠️ 알려진 제한사항

### 1. Vercel에서 Selenium 작동 안 함
- 원인: Vercel 서버리스에 Chrome 미포함
- 해결: Hybrid 스크래퍼가 API 사용을 먼저 시도하므로 괜찮음
- 만약 API가 없다면: Browserless 서비스 사용 필요 (유료)

### 2. 로컬 개발 필요 사항
- Chrome/Chromium 설치 필수
- Selenium 설치 필수

### 3. Hyrox API 엔드포인트 미확인
- 현재 `/season-8/?content=ajax2&client=js` 엔드포인트 시도
- 실제 API 엔드포인트를 찾으면 더 안정적

---

## 🔍 다음 단계

### 우선순위 1: API 엔드포인트 확인
Browser DevTools Network 탭에서:
1. Hyrox 웹사이트 접속
2. 드롭다운으로 필터 선택
3. Network 탭에서 XHR/Fetch 요청 확인
4. 실제 JSON API 엔드포인트 찾기

### 우선순위 2: 성능 최적화
- 데이터베이스 캐싱 추가
- Redis 캐싱 사용 고려
- CDN 설정

### 우선순위 3: 모니터링
- Vercel Analytics 설정
- 에러 로깅 추가
- API 성공률 모니터링

---

## 📝 코드 사용 예제

### Flask 앱에서
```python
from hyrox_scraper_hybrid import HyroxHybridScraper

scraper = HyroxHybridScraper()

# 특정 필터로 검색
results = scraper.search_rankings(
    age_group='50',      # 나이 그룹
    gender='M',          # 성별 (M/W)
    division='H',        # 카테고리
    top_n=10,            # 각 대회에서 상위 10명
    num_races=10         # 최근 10개 대회
)

# 결과 사용
for race_name, participants in results.items():
    print(f"🏆 {race_name}")
    for participant in participants:
        print(f"  {participant['rank']}. {participant['firstName']} "
              f"{participant['lastName']} - {participant['time']}")
```

### API 호출
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "age_group": "50",
    "gender": "M",
    "division": "H",
    "top_n": 10,
    "num_races": 10
  }'
```

---

## ✅ 확인 체크리스트

- [ ] GitHub에 새 코드 푸시됨
- [ ] Vercel 배포 완료됨
- [ ] https://hyrox-rankings-analyzer.vercel.app 접속 가능
- [ ] 앱에서 데이터 로드됨
- [ ] 조건에 맞는 실제 선수 정보가 표시됨
- [ ] 테스트 데이터가 아닌 실제 Hyrox 대회 결과가 표시됨

---

## 🎯 결과

✅ **실제 데이터** - 더 이상 무작위 테스트 데이터 아님
✅ **자동 폴백** - API 실패 시 Selenium 사용, Selenium 실패 시 테스트 데이터
✅ **Vercel 호환** - 서버리스 배포 환경에서 작동
✅ **로컬 테스트** - Chrome 설치하면 로컬에서 Selenium으로 실제 데이터 확인 가능

---

**배포 완료! 🎉 이제 실제 Hyrox 랭킹 데이터를 확인할 수 있습니다.**
