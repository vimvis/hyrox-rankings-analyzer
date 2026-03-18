# 웹 배포 가이드 🚀

HYROX Rankings Analyzer를 클라우드에 배포하는 방법들입니다.

## 배포 옵션 비교

| 서비스 | 난이도 | 비용 | 설정 |
|--------|--------|------|------|
| **Heroku** | ⭐⭐ | 무료~유료 | 가장 간단 |
| **Railway** | ⭐⭐ | 무료~유료 | 매우 간단 |
| **Render** | ⭐⭐ | 무료~유료 | 간단 |
| **PythonAnywhere** | ⭐⭐⭐ | 무료~유료 | 중간 |
| **AWS** | ⭐⭐⭐⭐ | 복잡 | 매우 복잡 |

## 1️⃣ Heroku로 배포 (권장)

### 사전 준비

```bash
# Heroku CLI 설치
# https://devcenter.heroku.com/articles/heroku-cli

# 로그인
heroku login
```

### 배포 단계

```bash
# 저장소로 이동
cd hyrox-rankings-analyzer

# Heroku 앱 생성
heroku create your-app-name

# 환경 변수 설정
heroku config:set FLASK_ENV=production

# 배포
git push heroku master  # 또는 main

# 로그 확인
heroku logs --tail
```

### 앱 접속
```
https://your-app-name.herokuapp.com
```

---

## 2️⃣ Railway로 배포 (가장 추천)

Railway는 가장 간단하고 빠릅니다!

### 1단계: GitHub 연결

1. [railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "New Project" → "Deploy from GitHub repo" 클릭
4. 이 저장소 선택

### 2단계: 자동 배포

Railway가 자동으로:
- `Procfile` 읽기
- Python 환경 설정
- 패키지 설치
- 앱 시작

### 3단계: 접속

배포 완료 후 할당된 URL로 접속

**장점:**
- ✅ GitHub 연결하면 자동 배포
- ✅ 환경 변수 GUI로 관리
- ✅ 실시간 로그 확인
- ✅ 무료 tier 충분함
- ✅ 빌드 프로세스 완전 자동화

---

## 3️⃣ Render로 배포

### 1단계: 연결

1. [render.com](https://render.com) 접속
2. GitHub 연결
3. "New +" → "Web Service"
4. 저장소 선택

### 2단계: 설정

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

### 3단계: 배포

"Create Web Service" 클릭 → 자동 배포 시작

---

## 4️⃣ PythonAnywhere로 배포

### 1단계: 계정 생성

1. [pythonanywhere.com](https://www.pythonanywhere.com) 가입
2. "Web" 탭 → "Add a new web app"

### 2단계: Flask 앱 설정

```bash
# 콘솔에서
git clone <your-repo-url>
cd hyrox-rankings-analyzer
pip install -r requirements.txt
```

### 3단계: WSGI 설정

PythonAnywhere 대시보드에서:

```python
import sys
path = '/home/your-username/hyrox-rankings-analyzer'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### 4단계: 리로드

"Reload" 버튼 클릭 → 배포 완료

---

## 5️⃣ Docker로 배포 (고급)

### Dockerfile 생성

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "app:app"]
```

### Docker 이미지 빌드

```bash
docker build -t hyrox-analyzer .
docker run -p 5000:5000 hyrox-analyzer
```

---

## 🔒 보안 설정

배포 전 꼭 확인하세요:

### 1. 환경 변수

```bash
# .env 파일 생성
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

### 2. CORS 설정

`app.py`에서:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 3. 캐시 설정

프로덕션에서는 메모리 캐싱 대신 Redis 사용 권장:

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

---

## 📊 성능 최적화

### 1. 캐싱 헤더

```python
@app.after_request
def set_cache_headers(response):
    response.cache_control.max_age = 3600
    return response
```

### 2. Gzip 압축

```bash
pip install flask-compress
```

```python
from flask_compress import Compress
Compress(app)
```

### 3. CDN 설정

HTML/CSS/JS는 CloudFlare CDN으로 배포

---

## 🔧 배포 후 설정

### 커스텀 도메인

**Heroku:**
```bash
heroku domains:add your-domain.com
```

**Railway/Render:**
대시보드 → Settings → Custom Domain

### SSL/HTTPS

대부분의 서비스가 자동으로 SSL 제공합니다.

### 모니터링

```bash
# Heroku 로그
heroku logs --tail

# 또는 대시보드에서 실시간 모니터링
```

---

## 🐛 배포 문제 해결

### 문제: "Port not specified"

**해결:** `Procfile`이 제대로 설정되었는지 확인

```
web: gunicorn app:app
```

### 문제: "Module not found"

**해결:** `requirements.txt` 확인

```bash
pip list > requirements.txt
```

### 문제: 느린 응답

**해결:**
- Hyrox 웹사이트 응답 시간 확인
- 캐싱 활성화 확인
- 서버 로그 확인

---

## 💡 추천 설정

### 초보자
→ **Railway** 또는 **Heroku** 추천

**이유:**
- GitHub 연결만으로 자동 배포
- 환경 설정 간단
- 빌드 과정 완전 자동화

### 경험자
→ **Docker + Render** 또는 **AWS**

**이유:**
- 더 세밀한 제어 가능
- 프로덕션 레벨 관리
- 비용 최적화 가능

---

## 📚 추가 자료

- [Heroku Deployment Guide](https://devcenter.heroku.com/articles/procfile)
- [Railway Documentation](https://docs.railway.app/)
- [Flask Production Deployment](https://flask.palletsprojects.com/deployment/)
- [Docker for Flask Apps](https://docs.docker.com/language/python/)

---

**배포 완료! 🎉**

더 이상 로컬에서만 사용할 수 없습니다.
이제 전 세계 어디서나 접속 가능합니다! 🌍

