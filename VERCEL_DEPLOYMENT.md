# Vercel 배포 가이드 🚀

HYROX Rankings Analyzer를 Vercel에 배포하는 완벽한 가이드

---

## ✨ Vercel의 장점

✅ **프론트엔드 + 백엔드 통합** - 하나의 플랫폼에서 모두 관리
✅ **자동 배포** - Git push만으로 자동 배포
✅ **무료 호스팅** - 무료 tier로 충분
✅ **빠른 속도** - CDN으로 글로벌 배포
✅ **환경 변수 관리** - GUI에서 쉽게 설정
✅ **실시간 로그** - 배포 상황 실시간 모니터링

---

## 🚀 5분 배포 (가장 간단)

### 1단계: Vercel 접속

[vercel.com](https://vercel.com) 접속 후 **"GitHub로 로그인"**

### 2단계: 프로젝트 배포

**"New Project"** → **`vimvis/hyrox-rankings-analyzer`** 선택

### 3단계: 배포 완료!

자동으로:
- Python 환경 설정 ✅
- 패키지 설치 ✅
- 앱 빌드 ✅
- 배포 ✅

→ **`https://hyrox-rankings-analyzer.vercel.app`** 에서 접속!

---

## 🔧 환경 변수 설정 (선택사항)

Vercel 대시보드에서:

1. **Settings** → **Environment Variables**
2. 다음 변수 추가:

```
FLASK_ENV=production
FLASK_DEBUG=false
```

---

## 📊 배포 후 확인

### 1. 앱 접속
```
https://hyrox-rankings-analyzer.vercel.app
```

### 2. API 테스트
```
https://hyrox-rankings-analyzer.vercel.app/api/stats
```

### 3. 로그 확인
Vercel 대시보드 → **"Deployments"** → 최신 배포 선택 → **"Logs"**

---

## 🔄 자동 업데이트

GitHub에 push하면 자동으로:
1. Vercel이 감지
2. 새 버전 빌드
3. 배포 완료

**예시:**
```bash
git add .
git commit -m "Update features"
git push origin main
```

→ Vercel이 자동으로 배포! 🚀

---

## 📝 주요 파일

| 파일 | 역할 |
|------|------|
| `vercel.json` | Vercel 빌드 설정 |
| `app.py` | Flask 백엔드 |
| `hyrox_app_v2.html` | 웹 인터페이스 |
| `requirements.txt` | 파이썬 패키지 |

---

## 🐛 문제 해결

### 문제: "Build failed"

**확인:**
1. `requirements.txt` 확인 (문법 오류 없는지)
2. 파이썬 버전 확인 (3.11 권장)
3. 로그 확인 (Vercel 대시보드)

### 문제: API 응답 없음

**확인:**
1. Flask 서버 로그 확인
2. 환경 변수 설정 확인
3. CORS 설정 확인

### 문제: HTML 파일 로드 안 됨

**해결:**
`vercel.json`의 routes 확인:
```json
{
  "src": "/(.*)",
  "dest": "app.py"
}
```

---

## 💡 팁

### 1. 커스텀 도메인

Vercel 대시보드:
1. **Settings** → **Domains**
2. **Add** → 도메인 입력
3. DNS 설정 완료

예: `hyrox-analyzer.yourdomain.com`

### 2. 프리뷰 배포

Pull Request마다 자동으로 프리뷰 URL 생성!

### 3. 환경별 배포

```
main → Production (vercel.app)
develop → Preview
```

---

## 🎯 다음 단계

### 기본 설정 완료 후:

1. ✅ 도메인 설정 (선택사항)
2. ✅ 모니터링 설정 (선택사항)
3. ✅ Analytics 확인 (선택사항)

---

## 📚 추가 자료

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/python)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)
- [Vercel Troubleshooting](https://vercel.com/docs/troubleshott/common-issues)

---

## ✨ 완료!

이제 **웹에서 바로 접속 가능**합니다! 🎉

```
https://hyrox-rankings-analyzer.vercel.app
```

아무 곳에서나, 누구나 접속 가능합니다! 🌍

---

**필요 시 언제든지 업데이트 가능합니다!** 🚀
