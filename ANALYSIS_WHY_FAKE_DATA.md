# 🔍 왜 가짜 데이터만 나오는가? 원인 분석

## 현재 상황
```
사용자: "여전히 기록이 전부 가짜인데..."
현상: 무작위로 생성된 이름과 기록들만 계속 표시됨
```

---

## 🎯 근본 원인 분석

### 1단계: 하이브리드 스크래퍼의 실패 흐름

```javascript
┌─────────────────────────────────────────┐
│ 1️⃣ API 직접 호출 시도                   │
│ GET /season-8/?content=ajax2&client=js  │
└─────────────────────────────────────────┘
           ❌ FAILED
           원인: API 응답 형식 오류
                 또는 엔드포인트 존재 안 함
                ↓
┌─────────────────────────────────────────┐
│ 2️⃣ Selenium WebDriver 시도             │
│ Chrome 브라우저로 JavaScript 렌더링     │
└─────────────────────────────────────────┘
           ❌ FAILED
           원인: Vercel 환경에 Chrome 없음
                ↓
┌─────────────────────────────────────────┐
│ 3️⃣ 테스트 데이터 폴백                   │
│ _generate_test_data() 호출              │
└─────────────────────────────────────────┘
           ✅ SUCCESS
           결과: 무작위로 생성된 이름 + 기록
                (John Smith, 00:45:23 등)
```

### 2단계: 왜 각 단계가 실패하는가?

#### ❌ API 호출 실패 원인
```python
# hyrox_scraper_hybrid.py의 _fetch_via_api() 메서드

def _fetch_via_api(self, race_name: str, age_group: str, gender: str):
    params = {
        'content': 'ajax2',           # ← 이 파라미터들이 실제가 아님
        'client': 'js',
        'race': race_name,
        'age_group': age_group,
        'gender': gender,
    }

    response = self.session.get(self.API_URL, params=params, timeout=10)
    response.raise_for_status()

    # ← 여기서 실패하거나 JSON 형식이 예상과 다름
```

**문제점:**
- ❓ 실제 API 엔드포인트가 무엇인지 모름
- ❓ GraphQL인지 REST인지 모름
- ❓ 응답 형식이 무엇인지 모름
- ❓ 필수 헤더나 토큰이 있는지 모름

#### ❌ Selenium 실패 원인
```
Vercel 환경
  ├─ Python 런타임: ✅ 있음
  ├─ Flask: ✅ 있음
  ├─ Selenium: ✅ 패키지 설치됨
  ├─ Chrome/Chromium: ❌ 없음 ← 이것이 문제!
  └─ WebDriver: ❌ 작동 불가능
```

**결과:** Selenium이 Chrome 없이 WebDriver를 시작할 수 없음

#### ✅ 테스트 데이터만 작동
```python
def _generate_test_data(self, count: int = 10) -> List[Dict]:
    TEST_FIRST_NAMES = ["Anna", "Bob", "Carlos", ...]  # ← 이것들이 나옴
    TEST_LAST_NAMES = ["Smith", "Johnson", ...]        # ← 이것들이 나옴

    for rank in range(1, count + 1):
        first_name = random.choice(self.TEST_FIRST_NAMES)
        last_name = random.choice(self.TEST_LAST_NAMES)
        # ...
        return results  # ← 100% 무작위 데이터
```

---

## 🕵️ 실제 Hyrox API를 찾기 위해 해야 할 것

### 옵션 1: 브라우저 DevTools로 분석 (가장 정확함)
```
1. https://results.hyrox.com/season-8/ 접속
2. F12 → Network 탭 열기
3. 드롭다운으로 필터 선택 (Race, Age, Gender 등)
4. Network 요청 확인:
   - XHR/Fetch 요청 찾기
   - URL 확인
   - Request Headers 확인
   - Response 형식 확인 (JSON/GraphQL 등)
5. 실제 API 엔드포인트 찾기
```

### 옵션 2: 웹사이트 소스 분석
```bash
# 페이지 소스에서 API 엔드포인트 찾기
# JavaScript 파일에서 axios/fetch 호출 분석
# GraphQL endpoint URL 찾기
```

### 옵션 3: 공식 API 문서 찾기
```
Hyrox 공식 홈페이지 → API 문서 또는 개발자 가이드
mika:timing (웹사이트에 사용된 플랫폼) → 공식 API
```

---

## 🛠️ 즉시 개선 방안

### 방법 1: 더 자세한 로깅으로 문제 추적 (임시)

`hyrox_scraper_hybrid.py`의 `_fetch_via_api()`를 수정:

```python
def _fetch_via_api(self, race_name: str, age_group: str, gender: str):
    try:
        print(f"    API 시도 중... (URL: {self.API_URL})", flush=True)
        response = self.session.get(self.API_URL, params=params, timeout=10)
        print(f"    상태 코드: {response.status_code}", flush=True)
        print(f"    응답 타입: {response.headers.get('content-type')}", flush=True)
        print(f"    응답 크기: {len(response.text)} bytes", flush=True)

        data = response.json()
        print(f"    JSON 파싱 성공. 키: {list(data.keys())}", flush=True)
        return self._parse_api_response(data)
    except Exception as e:
        print(f"    API 오류: {type(e).__name__}: {str(e)}", flush=True)
        return []
```

### 방법 2: 테스트 데이터 생성 직전에 경고 표시

`app.py`의 `/api/search` 엔드포인트에 경고 추가:

```python
@app.route('/api/search', methods=['POST'])
def search():
    # ...
    results = scraper.search_rankings(...)

    # 테스트 데이터만 사용되었는지 확인
    if all(all(r.get('firstName') in TEST_FIRST_NAMES for r in rankings)
           for rankings in results.values()):
        print("⚠️ 경고: 테스트 데이터만 반환되었습니다!")
        # 혹은 응답에 경고 메시지 추가

    return jsonify(results)
```

---

## 💡 올바른 해결책 (장기적)

### ✅ Best Practice: 실제 API 엔드포인트 사용

```python
class HyroxProperScraper:
    """Hyrox의 실제 API를 직접 사용"""

    REAL_API_URL = "https://results.hyrox.com/graphql"  # 예시
    # 또는
    REAL_API_URL = "https://api.hyrox.com/v1/rankings"  # 예시

    def fetch_rankings(self, race_id: str, age_group: str):
        query = {
            'query': '''
                query GetRankings($raceId: ID!, $ageGroup: String!) {
                    race(id: $raceId) {
                        rankings(ageGroup: $ageGroup) {
                            rank
                            participant {
                                firstName
                                lastName
                                nationality
                            }
                            time
                        }
                    }
                }
            ''',
            'variables': {
                'raceId': race_id,
                'ageGroup': age_group
            }
        }

        response = requests.post(self.REAL_API_URL, json=query)
        # ← 실제 데이터 반환
```

---

## 📊 테스트 데이터의 특징 (가짜인 이유)

### 생성되는 데이터의 패턴
```python
TEST_FIRST_NAMES = ["Anna", "Bob", "Carlos", "Diana", "Erik", "Fiona",
                    "Gustav", "Hannah", "Ivan", "Julia", "Klaus", "Laura",
                    "Marco", "Nora", "Oscar", "Paula"]

TEST_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                   "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
```

### 생성된 데이터의 특징
- ✅ 항상 같은 16개 이름에서만 선택
- ✅ 시간이 완전히 무작위 (00:00:00 ~ 02:59:59)
- ✅ 국적도 고정된 16개 중 선택
- ✅ 실제 대회 결과와 전혀 다름
- ✅ 랭킹 체계나 분포가 현실적이지 않음

---

## 🎯 왜 이렇게 구현했나?

**원래 의도:**
> "실제 API를 찾을 때까지의 임시 폴백"

**현실:**
> "API를 찾지 못해서 항상 테스트 데이터만 나옴"

---

## ✅ 다음 단계 (우선순위)

### 🥇 1순위: 실제 API 찾기
**방법:** 브라우저 DevTools의 Network 탭 사용
```
1. https://results.hyrox.com/season-8/ 열기
2. F12 → Network 탭
3. 필터 적용 → XHR 요청 확인
4. 실제 API 엔드포인트 확인
5. 응답 형식 분석
```

**예상 발견:**
- GraphQL endpoint (예: `/graphql`)
- REST API endpoint (예: `/api/rankings`)
- WebSocket connection (실시간 데이터)

### 🥈 2순위: API 구현
실제 API를 `HyroxProperScraper` 클래스로 구현

### 🥉 3순위: 배포
새로운 스크래퍼를 `app.py`에 통합

---

## 📝 결론

| 상태 | 설명 |
|------|------|
| ❌ **API 호출** | 실제 엔드포인트 정보 없음 |
| ❌ **Selenium** | Vercel에 Chrome 없음 |
| ✅ **테스트 데이터** | 무작위 생성 (이것만 작동) |

**결과:** 항상 가짜 데이터만 표시됨

**해결책:** 실제 API 엔드포인트를 찾아야 함 → DevTools Network 탭으로 분석 필요

---

## 🔗 다음 작업

사용자가 해야 할 것:
1. **브라우저 열기:** https://results.hyrox.com/season-8/
2. **개발자 도구 열기:** F12 또는 우클릭 → 검사
3. **Network 탭 클릭**
4. **필터 적용:** "race" 또는 "ranking" 검색
5. **실제 API 요청 찾기**
6. **나에게 알려주기:**
   - 실제 요청 URL
   - Request method (GET/POST)
   - Response 형식 (JSON/GraphQL)

또는 내가 할 수 있는 것:
- Browser DevTools 시뮬레이션 시도
- mika:timing 플랫폼 API 공식 문서 찾기
- 다른 스포츠 이벤트 결과 웹사이트와 비교
