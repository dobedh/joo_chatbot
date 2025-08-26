#!/usr/bin/env python3
"""
벡터 DB v3 재구축
완벽하게 구조화된 데이터로 벡터 DB 재생성
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.korean_vector_store import KoreanVectorStore
from src.smart_chunker import SmartChunker
import chromadb
from chromadb.config import Settings
import shutil


def rebuild_vector_database_v3():
    """개선된 데이터로 벡터 DB v3 재구축"""
    
    print("🚀 벡터 DB v3 재구축 시작...")
    
    # 1. 기존 DB 삭제
    chroma_path = project_root / "data" / "chroma_db"
    if chroma_path.exists():
        print("🗑️ 기존 벡터 DB 삭제 중...")
        shutil.rmtree(chroma_path)
    
    # 2. 새 벡터 스토어 초기화
    print("📦 새 벡터 스토어 초기화...")
    vector_store = KoreanVectorStore(
        persist_directory=str(chroma_path)
    )
    
    # 3. 스마트 청커 초기화 (최적화된 파라미터)
    print("✂️ 스마트 청커 초기화...")
    chunker = SmartChunker(
        chunk_size=1200,  # 최적화된 크기
        chunk_overlap=300  # 충분한 오버랩
    )
    
    # 4. 구조화된 문서 로드
    structured_file = project_root / "data" / "samsung_esg_final_v3.md"
    
    if not structured_file.exists():
        print(f"❌ 파일을 찾을 수 없음: {structured_file}")
        return
    
    print(f"📄 구조화된 문서 로드: {structured_file}")
    
    # 5. 청킹 수행
    print("✂️ 문서 청킹 중...")
    chunks = chunker.chunk_markdown(structured_file)
    print(f"✅ {len(chunks)} 개 청크 생성")
    
    # 6. 청크 품질 검증
    print("\n📊 청크 품질 검증:")
    
    # 주요 키워드 검증
    key_terms = [
        "개인정보보호 3대 원칙",
        "미주 2022년 39%",
        "DX부문",
        "HRA",
        "인권 교육",
        "95.7%",
        "재생에너지",
        "ESG"
    ]
    
    for term in key_terms:
        found_chunks = [i for i, chunk in enumerate(chunks) if term in chunk['content']]
        if found_chunks:
            print(f"  ✅ '{term}' 발견: {len(found_chunks)}개 청크")
        else:
            print(f"  ⚠️ '{term}' 미발견")
    
    # 7. 벡터 DB에 추가
    print("\n💾 벡터 DB에 청크 추가 중...")
    # chunks에서 texts와 metadatas 분리
    texts = [chunk['content'] for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        # 메타데이터에서 리스트를 문자열로 변환
        metadata = {}
        for key, value in chunk['metadata'].items():
            if isinstance(value, list):
                metadata[key] = ', '.join(str(v) for v in value)
            else:
                metadata[key] = value
        metadatas.append(metadata)
    vector_store.add_documents(texts, metadatas)
    
    # 8. 통계 출력
    print("\n📊 벡터 DB v3 구축 완료:")
    print(f"  - 총 청크 수: {len(chunks)}")
    print(f"  - 평균 청크 길이: {sum(len(c['content']) for c in chunks) / len(chunks):.0f}자")
    print(f"  - 최소 청크 길이: {min(len(c['content']) for c in chunks)}자")
    print(f"  - 최대 청크 길이: {max(len(c['content']) for c in chunks)}자")
    
    # 9. 테스트 검색
    print("\n🔍 테스트 검색 수행:")
    test_queries = [
        "개인정보보호 3대 원칙이 뭐야?",
        "미주 2022년 매출 비중은?",
        "HRA가 뭐야?",
        "인권 교육을 몇프로가 받았어?",
        "DX부문 2024년 매출은?"
    ]
    
    for query in test_queries:
        results = vector_store.similarity_search(query, k=3)
        if results:
            print(f"\n  Q: {query}")
            print(f"  A: {results[0].page_content[:100]}...")
            # 정답 포함 여부 체크
            if "개인정보보호" in query and "투명하게" in results[0].page_content:
                print("  ✅ 정답 포함")
            elif "미주" in query and "39" in results[0].page_content:
                print("  ✅ 정답 포함")
            elif "HRA" in query and ("Human Rights" in results[0].page_content or "인권" in results[0].page_content):
                print("  ✅ 정답 포함")
            elif "인권 교육" in query and "95.7" in results[0].page_content:
                print("  ✅ 정답 포함")
            elif "DX부문" in query and "166.32" in results[0].page_content:
                print("  ✅ 정답 포함")
        else:
            print(f"\n  Q: {query}")
            print(f"  A: 결과 없음 ❌")
    
    print("\n✅ 벡터 DB v3 재구축 완료!")
    print(f"📁 저장 위치: {chroma_path}")
    
    return vector_store


if __name__ == "__main__":
    rebuild_vector_database_v3()