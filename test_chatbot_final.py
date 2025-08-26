#!/usr/bin/env python3
"""
최종 챗봇 통합 테스트
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore
from src.gemini_rag_pipeline import GeminiRAGPipeline
from src.config import GOOGLE_API_KEY

def test_chatbot():
    """챗봇 통합 테스트"""
    
    print("=" * 70)
    print("🎯 삼성전자 ESG 챗봇 - 최종 테스트")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    
    print("\n📚 한국어 벡터 스토어 로딩...")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # RAG Pipeline 초기화
    print("🤖 Gemini 2.0 Flash RAG Pipeline 초기화...")
    rag_pipeline = GeminiRAGPipeline(
        vector_store=vector_store,
        model_name="gemini-2.0-flash-exp",
        temperature=0.7
    )
    
    # 테스트 질문들
    test_questions = [
        "2024년 삼성전자 매출은 얼마인가요?",
        "DX부문의 탄소중립 목표는 언제까지인가요?",
        "DS부문 재생에너지 전환율은 몇 퍼센트인가요?",
    ]
    
    print("\n💬 질의응답 테스트:")
    print("-" * 70)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 질문 {i}: {question}")
        
        try:
            response = rag_pipeline.query(question)
            
            if response and "answer" in response:
                answer = response["answer"]
                # 답변이 너무 길면 줄임
                if len(answer) > 200:
                    answer = answer[:200] + "..."
                
                print(f"✅ 답변: {answer}")
                
                # 출처 확인
                if response.get("sources"):
                    print(f"📚 참조: {len(response['sources'])}개 문서")
                    # 첫 번째 출처만 표시
                    first_source = response['sources'][0]
                    print(f"   - 페이지 {first_source['page']}: {first_source['content'][:100]}...")
            else:
                print("⚠️ 답변 없음")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)[:100]}")
    
    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("\n🚀 챗봇 상태:")
    print("   - API: Gemini 2.0 Flash (gemini-2.0-flash-exp)")
    print("   - 벡터 DB: 443개 문서 (ko-sroberta-multitask)")
    print("   - URL: http://localhost:8501")
    print("=" * 70)

if __name__ == "__main__":
    test_chatbot()