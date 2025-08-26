#!/usr/bin/env python3
"""
Korean Vector Store 검색 테스트
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore
from src.config import *

def test_korean_search():
    """한국어 검색 테스트"""
    
    print("=" * 60)
    print("🧪 한국어 벡터 검색 테스트")
    print("=" * 60)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    
    if not korean_db_path.exists():
        print("❌ 한국어 벡터 DB가 없습니다.")
        return
    
    print("📚 한국어 벡터 스토어 로딩 중...")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # 통계 확인
    stats = vector_store.get_statistics()
    print(f"\n📊 벡터 DB 통계:")
    print(f"  총 문서: {stats['total_documents']}개")
    print(f"  임베딩 차원: {stats['embedding_dimension']}")
    
    # 테스트 쿼리들
    test_queries = [
        "DX부문 탄소중립 목표",
        "2024년 매출 실적",
        "DS 반도체 사업",
        "재생에너지 전환율",
        "CEO 메시지 요약"
    ]
    
    print("\n" + "=" * 60)
    print("🔍 검색 테스트")
    print("-" * 60)
    
    for query in test_queries:
        print(f"\n📝 쿼리: '{query}'")
        
        # 검색 실행
        results = vector_store.similarity_search(query, k=3)
        
        if results:
            print(f"✅ {len(results)}개 결과 찾음:")
            
            for i, doc in enumerate(results[:2], 1):  # 상위 2개만 표시
                print(f"\n  [{i}] 페이지 {doc.metadata.get('page', 'N/A')}, "
                      f"섹션: {doc.metadata.get('section', 'N/A')}")
                print(f"      타입: {doc.metadata.get('chunk_type', 'N/A')}")
                print(f"      내용: {doc.page_content[:100]}...")
                
                # 거리 정보 표시
                if 'distance' in doc.metadata:
                    print(f"      거리: {doc.metadata['distance']:.4f}")
        else:
            print("❌ 검색 결과 없음")
    
    # 약어 테스트
    print("\n" + "=" * 60)
    print("🔤 약어 확장 테스트")
    print("-" * 60)
    
    abbreviation_queries = [
        "DX",  # -> DX(디바이스경험부문)
        "CEO",  # -> CEO(최고경영자)
        "ESG"   # -> ESG(환경사회거버넌스)
    ]
    
    for query in abbreviation_queries:
        enhanced = vector_store.enhance_query(query)
        print(f"원본: '{query}' → 확장: '{enhanced}'")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_korean_search()