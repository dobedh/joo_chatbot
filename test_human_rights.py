#!/usr/bin/env python3
"""
인권 교육 검색 테스트
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from src.korean_vector_store import KoreanVectorStore

def test_human_rights_search():
    """인권 교육 검색 테스트"""
    
    print("=" * 70)
    print("🔍 인권 교육 검색 테스트")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    print("\n📚 벡터 스토어 로딩...")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # 다양한 쿼리 테스트
    test_queries = [
        "인권 교육을 몇프로가 받았어?",
        "인권 교육 수료율",
        "95.7% 인권 교육",
        "직원 인권 교육",
        "2024년 인권 교육",
        "온라인 오프라인 수료율"
    ]
    
    for query in test_queries:
        print(f"\n📝 쿼리: '{query}'")
        print("-" * 50)
        
        results = vector_store.similarity_search(query, k=3)
        
        if results:
            for i, doc in enumerate(results, 1):
                print(f"\n[{i}] 페이지 {doc.metadata.get('page')}, 섹션: {doc.metadata.get('section')}")
                content = doc.page_content
                
                # 95.7%가 포함되어 있는지 확인
                if "95.7%" in content:
                    print("✅ 정답 포함!")
                    print(f"내용: {content[:200]}...")
                else:
                    print(f"내용: {content[:100]}...")
        else:
            print("❌ 검색 결과 없음")
    
    print("\n" + "=" * 70)
    print("✅ 테스트 완료")

if __name__ == "__main__":
    test_human_rights_search()