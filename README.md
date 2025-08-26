# 🌱 삼성전자 ESG AI 챗봇

삼성전자 2025년 지속가능경영보고서를 기반으로 한 AI 챗봇입니다.

## ✨ 주요 기능

- 📱 **모바일 최적화 UI**: 모든 디바이스에서 완벽하게 작동
- 🤖 **RAG 기반 질의응답**: 정확한 문서 기반 답변
- 📚 **출처 표시**: 모든 답변에 대한 페이지 참조
- 💬 **대화 기록 관리**: 컨텍스트 유지 및 대화 초기화
- ⚡ **빠른 응답**: 벡터 DB를 통한 효율적인 검색

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 이동
cd samsung_chatbot

# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 Google API 키를 입력:

```bash
cp .env.example .env
# .env 파일을 편집하여 GOOGLE_API_KEY 입력
```

### 3. 실행

#### 방법 1: 스크립트 사용 (권장)
```bash
./run.sh
```

#### 방법 2: 직접 실행
```bash
streamlit run src/app_gemini.py
```

### 4. 접속

- 로컬: http://localhost:8501
- 모바일: http://[YOUR_IP]:8501

## 📱 모바일 접속

같은 네트워크에 있는 모바일 기기에서 접속하려면:

1. 컴퓨터의 IP 주소 확인:
   ```bash
   # macOS/Linux
   ifconfig | grep inet
   
   # Windows
   ipconfig
   ```

2. 모바일 브라우저에서 접속:
   ```
   http://[컴퓨터_IP]:8501
   ```

## 🏗️ 프로젝트 구조

```
samsung_chatbot/
├── src/
│   ├── app.py              # Streamlit 메인 앱
│   ├── config.py           # 설정 관리
│   ├── pdf_processor.py    # PDF 처리
│   ├── vector_store.py     # 벡터 DB 관리
│   └── rag_pipeline.py     # RAG 파이프라인
├── data/
│   └── chroma_db/          # 벡터 DB 저장소
├── config/                 # 설정 파일
├── requirements.txt        # 의존성
└── .env                    # 환경 변수
```

## 🔧 설정

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `LLM_MODEL`: 사용할 모델 (기본: gpt-4-turbo-preview)
- `TEMPERATURE`: 응답 창의성 (0.0-1.0, 기본: 0.7)
- `CHUNK_SIZE`: 문서 청크 크기 (기본: 1000)
- `CHUNK_OVERLAP`: 청크 중첩 (기본: 200)

## 💡 사용 예시

**질문할 수 있는 내용:**
- "삼성전자의 탄소중립 목표는 무엇인가요?"
- "순환경제를 위한 활동을 알려주세요"
- "ESG 경영 전략을 설명해주세요"
- "재생에너지 사용 현황은 어떻게 되나요?"

## 🛠️ 문제 해결

### OpenAI API 키 오류
`.env` 파일에 올바른 API 키가 입력되었는지 확인

### PDF 파일을 찾을 수 없음
`Samsung_Electronics_Sustainability_Report_2025_KOR.pdf` 파일이 프로젝트 상위 디렉토리에 있는지 확인

### 메모리 부족
`CHUNK_SIZE`를 줄이거나 배치 크기 조정

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.