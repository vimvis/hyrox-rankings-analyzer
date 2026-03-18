# 🔍 근본 원인 분석 완료

## 🎯 최종 결론

**가짜 데이터가 나오는 이유:**

```
API 파라미터 형식이 잘못됨 → API 호출 실패 → Selenium도 실패 → 테스트 데이터만 사용
```

---

## 📊 증거와 분석

### 1단계: API 엔드포인트 확인
✅ **실제로 존재함**
```
URL: https://results.hyrox.com/season-8/?content=ajax2&client=js
메서드: GET
상태: 200 OK
```

### 2단계: URL 파라미터 분석

**웹사이트가 실제로 사용하는 파라미터:**
```
https://results.hyrox.com/season-8/index.php?pid=list&pidp=start
&search%5Bsex%5D=M              ← M (남자) 또는 W (여자)
&search%5Bage_class%5D=%25      ← % (모두) 또는 50, 40 등
```

**디코딩하면:**
```
search[sex]=M
search[age_class]=%
```

### 3단계: Division/Race ID 확인

각 대회마다 **고유한 ID**가 있음:
```
"HYROX ELITE 15 - Saturday" → HE_LR3MS4JI1404
"HYROX - Saturday" → H_LR3MS4JI1402
"HYROX DOUBLES - Saturday" → HD_LR3MS4JI1402
"HYROX PRO - Sunday" → HPRO_LR3MS4JI128C
```

---

## ❌ 하이브리드 스크래퍼의 문제점

### 현재 코드 (잘못됨)
```python
def _fetch_via_api(self, race_name: str, age_group: str, gender: str):
    params = {
        'content': 'ajax2',           # ✅ 올바름
        'client': 'js',               # ✅ 올바름
        'race': race_name,            # ❌ 잘못됨 (문자열이 아닌 ID 필요)
        'age_group': age_group,       # ❌ 파라미터명 잘못됨 (search[age_class] 필요)
        'gender': gender,             # ❌ 파라미터명 잘못됨 (search[sex] 필요)
    }

    response = self.session.get(self.API_URL, params=params, timeout=10)
    # ← 여기서 실패 (API가 인식 못함)
```

### 올바른 파라미터 형식
```python
params = {
    'content': 'ajax2',              # ✅ 올바름
    'client': 'js',                  # ✅ 올바름
    'search[sex]': 'M',              # ✅ 올바른 파라미터명
    'search[age_class]': '50',       # ✅ 올바른 파라미터명
    'search[event]': 'H_LR3MS4JI1402',  # ✅ Division ID 필요
}
```

---

## 🔄 데이터 흐름 다이어그램

### 가짜 데이터가 생성되는 경로

```
사용자 요청
    ↓
app.py: search_rankings() 호출
    ↓
hyrox_scraper_hybrid.py: search_rankings() 호출
    ↓
fetch_race_results() 호출 (각 대회별)
    ↓
┌──────────────────────────────────────┐
│ 1️⃣ _fetch_via_api() 시도            │
│   params = {                         │
│     'race': race_name,       ❌      │
│     'gender': gender,        ❌      │
│     'age_group': age_group,  ❌      │
│   }                                  │
│   → API 응답: 없음 또는 오류         │
└──────────────────────────────────────┘
    ↓ 실패
┌──────────────────────────────────────┐
│ 2️⃣ _fetch_via_selenium() 시도       │
│   Chrome WebDriver 시작              │
│   → 오류: Chrome 없음 (Vercel)       │
└──────────────────────────────────────┘
    ↓ 실패
┌──────────────────────────────────────┐
│ 3️⃣ _generate_test_data() 호출       │
│   무작위 선수 생성                   │
│   names = ["Anna", "Bob", ...]  ❌   │
│   times = random(00:00:00~02:59) ❌  │
│   → 100% 가짜 데이터 반환           │
└──────────────────────────────────────┘
    ↓
사용자에게 가짜 데이터 표시
```

---

## ✅ 해결책

### API 파라미터 올바르게 수정

```python
def _fetch_via_api(self, race_name: str, age_group: str, gender: str, division_id: str):
    """올바른 파라미터로 API 호출"""

    # Age class 매핑
    age_class_mapping = {
        'All': '%',
        '50-54': '50',
        '40-44': '40',
        # ...
    }

    # Gender 매핑
    sex_mapping = {
        'M': 'M',
        'W': 'W',
        'All': '%'
    }

    params = {
        'content': 'ajax2',              # ✅
        'client': 'js',                  # ✅
        'search[sex]': sex_mapping[gender],        # ✅ 올바른 파라미터
        'search[age_class]': age_class_mapping[age_group],  # ✅ 올바른 파라미터
        'search[event]': division_id,    # ✅ Division ID (필요하면)
    }

    response = self.session.get(self.API_URL, params=params, timeout=10)
    response.raise_for_status()

    # 실제 API 응답 파싱
    data = response.json()
    return self._parse_api_response(data)
```

---

## 🧪 검증 결과

### API가 정상 작동하는 증거
1. ✅ Status Code 200 반환
2. ✅ 필터 변경 시 새로운 요청 발생
3. ✅ 데이터가 없으면 "There are currently no results available" 메시지
4. ✅ URL에 올바른 파라미터 형식 확인: `search[sex]=M&search[age_class]=%`

### 현재 스크래퍼의 문제
1. ❌ API 파라미터명 오류
2. ❌ Vercel에서 Selenium 불가능
3. ❌ 테스트 데이터 폴백만 작동

---

## 🔧 다음 단계

### 긴급 수정 사항

**파일:** `hyrox_scraper_hybrid.py`

변경 전:
```python
params = {
    'content': 'ajax2',
    'client': 'js',
    'race': race_name,
    'age_group': age_group,
    'gender': gender,
}
```

변경 후:
```python
params = {
    'content': 'ajax2',
    'client': 'js',
    'search[sex]': self._map_gender(gender),
    'search[age_class]': self._map_age_group(age_group),
}
```

### 매핑 함수 추가

```python
def _map_gender(self, gender: str) -> str:
    mapping = {'M': 'M', 'W': 'W', 'All': '%'}
    return mapping.get(gender, '%')

def _map_age_group(self, age_group: str) -> str:
    mapping = {
        'All': '%',
        '16-24': '16',
        '25-29': '25',
        '30-34': '30',
        '35-39': '35',
        '40-44': '40',
        '45-49': '45',
        '50-54': '50',
        '55-59': '55',
        '60-64': '60',
        '65-69': '65',
        '70-74': '70',
        '75-79': '75',
    }
    return mapping.get(age_group, '%')
```

---

## 📈 예상 결과

### 수정 후
```
✅ API 호출 성공
   → 실제 Hyrox 데이터 반환
   → 테스트 데이터 폴백 불필요
```

### 로그 예상 출력
```
🔍 10개 대회에서 데이터 수집 중...

  🔄 2025 Verona 데이터 로드 중... ✅ API로 24명 수집
  🔄 2025 London Excel 데이터 로드 중... ✅ API로 22명 수집
  🔄 2025 Melbourne 데이터 로드 중... ✅ API로 20명 수집
  ...

📊 결과:
📍 2025 Verona:
   1. Zeitler, Sarah - USA - 108:08.06  ← 실제 데이터
   2. Manna, Cassidy - USA - 59:10.66   ← 실제 데이터
   3. Williams, Devon - USA - 118:04.37 ← 실제 데이터
   ...
```

---

## 🎯 핵심 요약

| 항목 | 이전 | 현재 | 해결책 |
|------|------|------|--------|
| API 파라미터 | ❌ race, gender, age_group | ❓ 불명확함 | ✅ search[sex], search[age_class] |
| API 작동 | ❌ 실패 | ✅ 실제로 작동함 | ✅ 파라미터 수정 |
| 데이터 | ❌ 가짜 | ❌ 여전히 가짜 | ✅ 실제 데이터 |

---

## 📝 결론

**문제의 핵심:**
- API는 정상적으로 작동함
- **파라미터 형식만 잘못됨**
- 파라미터를 올바르게 수정하면 실제 데이터를 받을 수 있음

**다음 작업:**
1. `hyrox_scraper_hybrid.py`의 `_fetch_via_api()` 메서드 수정
2. 파라미터 매핑 함수 추가
3. 로컬 테스트
4. GitHub 푸시
5. Vercel 재배포
