#!/usr/bin/env python3
"""
RAG 시스템 디버깅 스크립트
벡터 검색이 제대로 작동하는지 확인
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import *
from src.gemini_vector_store import GeminiVectorStore

def debug_vector_search():
    print("🔍 RAG 시스템 디버깅 시작...")
    
    # Initialize vector store
    vector_store = GeminiVectorStore(
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )
    
    if not vector_store.exists():
        print("❌ 벡터 DB가 존재하지 않습니다!")
        return
    
    # Check document count
    doc_count = vector_store.collection.count()
    print(f"📚 벡터 DB에 저장된 문서 수: {doc_count}")
    
    # Test queries
    test_queries = [
        "삼성전자",
        "ESG", 
        "지속가능경영",
        "탄소중립",
        "공급망",
        "제3자 검증"
    ]
    
    for query in test_queries:
        print(f"\n🔍 검색어: '{query}'")
        
        # Search
        results = vector_store.similarity_search(query, k=3)
        
        print(f"📝 검색 결과 수: {len(results)}")
        
        for i, doc in enumerate(results[:2]):  # Show top 2
            print(f"\n--- 결과 {i+1} ---")
            print(f"페이지: {doc.metadata.get('page', 'Unknown')}")
            print(f"내용 미리보기: {doc.page_content[:200]}...")
    
    print("\n✅ 디버깅 완료!")

if __name__ == "__main__":
    debug_vector_search()