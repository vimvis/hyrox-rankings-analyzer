@echo off
REM HYROX Rankings Analyzer 실행 스크립트 (Windows)

echo.
echo 🏃 HYROX Rankings Analyzer 시작...
echo.

REM 가상 환경 확인
if not exist "venv" (
    echo 📦 가상 환경 생성 중...
    python -m venv venv
)

REM 가상 환경 활성화
call venv\Scripts\activate.bat

REM 패키지 설치
if not exist ".installed" (
    echo 📦 필수 패키지 설치 중...
    pip install -r requirements.txt
    type nul > .installed
)

REM Flask 앱 실행
echo.
echo 🚀 Flask 서버 시작...
echo 📍 접속 주소: http://localhost:5000
echo ⏹️  종료하려면 Ctrl+C를 누르세요
echo.

python app.py

pause
