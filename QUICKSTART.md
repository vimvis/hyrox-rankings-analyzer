# 빠른 시작 가이드 🚀

HYROX Rankings Analyzer를 5분 안에 실행하세요!

## 📋 요구사항

- Python 3.8 이상
- 인터넷 연결

## 🚀 Windows 사용자

1. **파일 다운로드**
   - 모든 파일을 한 폴더에 저장하세요

2. **실행**
   - `run.bat` 파일을 더블클릭하세요
   - 자동으로 패키지 설치 및 서버 시작

3. **접속**
   - 브라우저에서 `http://localhost:5000` 접속

## 🚀 macOS / Linux 사용자

1. **파일 다운로드**
   ```bash
   # 또는 git clone으로 받아도 됩니다
   cd ~/Downloads/hyrox-analyzer
   ```

2. **권한 설정 및 실행**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **접속**
   - 브라우저에서 `http://localhost:5000` 접속

## 🔍 사용 방법

### 예시: 50-54세 남자 싱글 Top 10 검색

1. **필터 설정**
   - 나이 그룹: `50-54` ✓
   - 성별: `남자` ✓
   - 카테고리: `HYROX (싱글)` ✓
   - Top N: `10` (기본값)
   - 최근 대회 수: `10` (기본값)

2. **검색 시작**
   - "🔍 검색 시작" 버튼 클릭
   - 5-10초 대기 (첫 검색 시)

3. **결과 확인**
   - 최근 10개 대회의 결과 확인
   - CSV 다운로드 또는 인쇄 가능

## 🎯 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 필터 검색 | 나이, 성별, 카테고리로 선수 검색 |
| 📊 종합 결과 | 여러 대회의 결과를 한곳에서 비교 |
| 📥 CSV 내보내기 | 엑셀에서 추가 분석 가능 |
| 🖨️ 인쇄 | 결과를 PDF 또는 인쇄 |
| ⚡ 캐싱 | 동일 검색은 1초 이내 |

## ❓ 문제 해결

### 문제: "Port 5000 is already in use"

**해결:**
```bash
# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 문제: "ModuleNotFoundError"

**해결:**
```bash
pip install -r requirements.txt
```

### 문제: 데이터가 로드되지 않음

- Hyrox 웹사이트가 정상 작동하는지 확인
- 인터넷 연결 확인
- 브라우저 콘솔(F12) 확인

## 🌐 접속 주소

| 역할 | 주소 |
|------|------|
| 웹 앱 | http://localhost:5000 |
| API | http://localhost:5000/api |

## 🔌 API 사용 예시

```bash
# 50-54세 남자 싱글 Top 10 검색
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

## 📚 추가 정보

- 전체 설명서: [README.md](README.md)
- 기술 문서: 소스 코드 주석 참고

## 💡 팁

1. **캐싱 활용**: 같은 검색을 하면 1초 안에 결과 출력
2. **CSV 내보내기**: 엑셀에서 자유롭게 정렬/필터링 가능
3. **인쇄**: Ctrl+P로 PDF로 저장 가능

## 🆘 지원

- README.md의 "문제 해결" 섹션 참고
- 소스 코드의 주석 확인
- Flask/Python 공식 문서 참고

---

**Happy Racing! 🏃💨**

