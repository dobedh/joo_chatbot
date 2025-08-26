#!/usr/bin/env python3
"""
디버깅 정보와 함께 테스트
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore
from src.gemini_rag_pipeline import GeminiRAGPipeline

def test_with_debug():
    """디버깅 정보와 함께 테스트"""
    
    print("=" * 70)
    print("🔍 디버깅 모드 테스트")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    print("\n📚 벡터 스토어 로딩...")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # RAG Pipeline 초기화 (Gemini 2.0 Flash)
    print("🤖 Gemini 2.0 Flash 초기화...")
    rag_pipeline = GeminiRAGPipeline(
        vector_store=vector_store,
        model_name="gemini-2.0-flash-exp",
        temperature=0.7
    )
    
    # 테스트 질문
    test_question = "2024년 매출은?"
    
    print(f"\n💬 질문: {test_question}")
    print("=" * 70)
    
    # 쿼리 실행 (디버깅 정보가 자동으로 출력됨)
    response = rag_pipeline.query(test_question)
    
    print("\n📝 최종 답변:")
    print(response["answer"][:300] if len(response["answer"]) > 300 else response["answer"])
    
    print("\n" + "=" * 70)
    print("✅ 위의 디버깅 정보에서 사용된 5개 문서를 확인할 수 있습니다.")

if __name__ == "__main__":
    test_with_debug()