#!/bin/bash

# HYROX Rankings Analyzer 실행 스크립트

echo "🏃 HYROX Rankings Analyzer 시작..."

# 가상 환경 확인
if [ ! -d "venv" ]; then
    echo "📦 가상 환경 생성 중..."
    python3 -m venv venv
fi

# 가상 환경 활성화
source venv/bin/activate

# 패키지 설치
if [ ! -f ".installed" ]; then
    echo "📦 필수 패키지 설치 중..."
    pip install -r requirements.txt
    touch .installed
fi

# Flask 앱 실행
echo "🚀 Flask 서버 시작..."
echo "📍 접속 주소: http://localhost:5000"
echo "⏹️  종료하려면 Ctrl+C를 누르세요"
echo ""

python app.py
