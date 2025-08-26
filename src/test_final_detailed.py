#!/usr/bin/env python3
"""
최종 테스트 - 상세 검증
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore

def test_final_detailed():
    """상세 검증"""
    
    print("=" * 70)
    print("🔍 상세 검색 결과 확인")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # 상세 검색 테스트
    test_queries = [
        "2024년 매출",
        "DX부문 탄소중립 2030",
        "DS부문 재생에너지 전환율",
        "CEO 메시지",
    ]
    
    for query in test_queries:
        print(f"\n📝 쿼리: '{query}'")
        results = vector_store.similarity_search(query, k=2)
        
        if results:
            for i, doc in enumerate(results, 1):
                print(f"\n[결과 {i}]")
                print(f"페이지: {doc.metadata.get('page')}, 섹션: {doc.metadata.get('section')}")
                print(f"내용 미리보기: {doc.page_content[:150]}...")
                
                # 메타데이터에서 metrics 확인
                if doc.metadata.get('metrics'):
                    print(f"수치 정보: {doc.metadata['metrics'][:100]}")
        else:
            print("결과 없음")
    
    return True

if __name__ == "__main__":
    test_final_detailed()