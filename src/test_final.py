#!/usr/bin/env python3
"""
최종 테스트 - Korean Vector Store 검증
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore

def test_final():
    """최종 시스템 검증"""
    
    print("=" * 70)
    print("🎯 삼성전자 ESG 한국어 챗봇 - 최종 검증")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    
    print("\n📚 한국어 벡터 스토어 로드 중...")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # 통계
    stats = vector_store.get_statistics()
    print(f"\n✅ 벡터 DB 상태:")
    print(f"   총 문서: {stats['total_documents']}개")
    print(f"   임베딩: ko-sroberta-multitask ({stats['embedding_dimension']}차원)")
    print(f"   섹션: {stats['unique_sections']}개")
    
    # 핵심 검색 테스트
    print("\n🔍 핵심 검색 검증:")
    test_queries = [
        ("2024년 매출", "174조"),
        ("DX부문 탄소중립", "2030"),
        ("DS부문 재생에너지", "24.8"),
        ("CEO", "CEO(최고경영자)"),
    ]
    
    success_count = 0
    for query, expected in test_queries:
        results = vector_store.similarity_search(query, k=1)
        if results:
            content = results[0].page_content
            if expected in content or expected in str(results[0].metadata):
                print(f"   ✅ '{query}' → 예상 결과 포함")
                success_count += 1
            else:
                print(f"   ⚠️ '{query}' → 예상 결과 미포함")
        else:
            print(f"   ❌ '{query}' → 검색 실패")
    
    print(f"\n📊 검색 성공률: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.0f}%)")
    
    # 최종 상태 확인
    print("\n" + "=" * 70)
    print("🏁 최종 검증 결과")
    print("=" * 70)
    
    if stats['total_documents'] == 443 and success_count >= 3:
        print("""
✅ 시스템 준비 완료!

🎯 구현 완료 항목:
• 한국어 최적화 벡터 DB (ko-sroberta-multitask)
• 스마트 청킹 (443개 청크)
• 텍스트 전처리 (약어 확장, 동의어 매핑)
• Streamlit 모바일 최적화 UI
• Google Gemini RAG 파이프라인

🚀 앱 실행 중: http://localhost:8501

💡 사용 가능한 질문 예시:
• DX부문의 2030년 탄소중립 목표는?
• 2024년 매출 실적을 알려주세요
• DS부문 반도체 사업의 재생에너지 전환율은?
• 삼성전자의 ESG 전략은 무엇인가요?
        """)
        return True
    else:
        print("\n⚠️ 일부 검증 실패. 시스템 점검 필요.")
        return False

if __name__ == "__main__":
    success = test_final()
    sys.exit(0 if success else 1)