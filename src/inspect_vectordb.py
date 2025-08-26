#!/usr/bin/env python3
"""
벡터 DB 내용 검사 스크립트
저장된 데이터의 형태와 내용을 자세히 확인
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import *
from src.gemini_vector_store import GeminiVectorStore

def inspect_vector_db():
    print("🔍 벡터 DB 내용 검사 시작...")
    print("=" * 60)
    
    # Initialize vector store
    vector_store = GeminiVectorStore(
        persist_directory=CHROMA_PERSIST_DIRECTORY
    )
    
    if not vector_store.exists():
        print("❌ 벡터 DB가 존재하지 않습니다!")
        return
    
    # 1. 기본 정보
    doc_count = vector_store.collection.count()
    print(f"📊 총 문서 수: {doc_count}")
    print("-" * 60)
    
    # 2. 첫 5개 문서 샘플 가져오기
    print("📝 문서 샘플 (처음 5개):")
    print("-" * 60)
    
    # Get all data (limited to first 5)
    all_data = vector_store.collection.get(
        limit=5,
        include=['documents', 'metadatas', 'embeddings']
    )
    
    for i, (doc_id, document, metadata) in enumerate(zip(
        all_data['ids'], 
        all_data['documents'], 
        all_data['metadatas']
    )):
        print(f"\n📄 문서 {i+1}:")
        print(f"   ID: {doc_id}")
        print(f"   메타데이터: {json.dumps(metadata, ensure_ascii=False, indent=2)}")
        print(f"   내용 길이: {len(document)} 문자")
        print(f"   내용 미리보기:")
        print(f"   「{document[:300]}...」")
        
        # 임베딩 정보 (차원만 확인)
        try:
            if all_data['embeddings']:
                embedding_dim = len(all_data['embeddings'][i]) if i < len(all_data['embeddings']) else 0
                print(f"   임베딩 차원: {embedding_dim}")
        except:
            print(f"   임베딩: 정보 확인 불가")
        
        print("-" * 40)
    
    # 3. 페이지별 분포 확인
    print("\n📊 페이지별 문서 분포:")
    print("-" * 60)
    
    # Get all metadata
    all_metadata = vector_store.collection.get(
        include=['metadatas']
    )['metadatas']
    
    # Count by page
    page_counts = {}
    for metadata in all_metadata:
        page = metadata.get('page', 'Unknown')
        page_counts[page] = page_counts.get(page, 0) + 1
    
    # Sort by page number
    sorted_pages = sorted(page_counts.items(), key=lambda x: (str(x[0]).isnumeric(), int(x[0]) if str(x[0]).isnumeric() else float('inf'), x[0]))
    
    for page, count in sorted_pages[:20]:  # Show first 20 pages
        print(f"   페이지 {page}: {count}개 청크")
    
    if len(sorted_pages) > 20:
        print(f"   ... 총 {len(sorted_pages)}개 페이지")
    
    # 4. 문서 길이 통계
    print(f"\n📏 문서 길이 통계:")
    print("-" * 60)
    
    all_docs = vector_store.collection.get(include=['documents'])['documents']
    doc_lengths = [len(doc) for doc in all_docs]
    
    print(f"   평균 길이: {sum(doc_lengths) / len(doc_lengths):.1f} 문자")
    print(f"   최소 길이: {min(doc_lengths)} 문자")
    print(f"   최대 길이: {max(doc_lengths)} 문자")
    
    # 5. 키워드 검색 테스트
    print(f"\n🔍 키워드 검색 테스트:")
    print("-" * 60)
    
    test_keywords = ["삼성전자", "ESG", "탄소", "환경", "지속가능"]
    
    for keyword in test_keywords:
        # Simple text search in documents
        matching_docs = []
        for i, doc in enumerate(all_docs):
            if keyword in doc:
                matching_docs.append(i)
        
        print(f"   '{keyword}' 포함 문서: {len(matching_docs)}개")
        
        if matching_docs:
            # Show one example
            sample_idx = matching_docs[0]
            sample_metadata = all_metadata[sample_idx]
            print(f"     예시: 페이지 {sample_metadata.get('page', 'Unknown')}")
    
    print("\n✅ 벡터 DB 검사 완료!")

if __name__ == "__main__":
    inspect_vector_db()