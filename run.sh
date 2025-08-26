#!/bin/bash

# Samsung Chatbot Runner Script

echo "🚀 Samsung Sustainability AI Assistant 시작 중..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 의존성 설치 중..."
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "❗ .env 파일에 OpenAI API 키를 입력해주세요!"
    exit 1
fi

# Check if API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ OpenAI API 키가 설정되지 않았습니다!"
    echo "📝 .env 파일을 열어 OPENAI_API_KEY를 설정해주세요."
    exit 1
fi

# Create necessary directories
mkdir -p data/chroma_db
mkdir -p config/personas
mkdir -p config/prompts

# Run the Streamlit app
echo "✅ 챗봇을 시작합니다..."
echo "🌐 브라우저에서 http://localhost:8501 으로 접속하세요"
echo "📱 모바일에서 접속하려면 http://[YOUR_IP]:8501 을 사용하세요"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0