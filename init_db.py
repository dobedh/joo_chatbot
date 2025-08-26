#!/usr/bin/env python3
"""
Streamlit Cloud용 DB 초기화 스크립트
첫 실행시 ChromaDB를 생성합니다.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.smart_chunker import SmartChunker
from src.korean_vector_store import KoreanVectorStore
import os
import shutil

def initialize_db():
    """ChromaDB 초기화"""
    print("🔄 ChromaDB 초기화 시작...")
    
    # DB 경로 설정
    db_path = Path("data/chroma_db_korean")
    
    # 이미 존재하면 스킵
    if db_path.exists() and len(list(db_path.iterdir())) > 0:
        print("✅ DB가 이미 존재합니다.")
        return True
    
    # 데이터 파일 확인
    data_file = Path("data/samsung_esg_final_v3.md")
    if not data_file.exists():
        print("❌ 데이터 파일이 없습니다:", data_file)
        return False
    
    print("📦 새 벡터 스토어 생성 중...")
    
    # 벡터 스토어 초기화
    vector_store = KoreanVectorStore(
        persist_directory=str(db_path)
    )
    
    # SmartChunker로 청킹
    print("✂️ 문서 청킹 중...")
    chunker = SmartChunker(
        chunk_size=1200,
        chunk_overlap=300
    )
    chunks = chunker.chunk_markdown(data_file)
    print(f"✅ {len(chunks)}개 청크 생성")
    
    # 벡터 DB에 추가
    print("💾 벡터 DB에 저장 중...")
    texts = [chunk['content'] for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        metadata = {}
        for key, value in chunk['metadata'].items():
            if isinstance(value, list):
                metadata[key] = ', '.join(str(v) for v in value)
            else:
                metadata[key] = value
        metadatas.append(metadata)
    
    vector_store.add_documents(texts, metadatas)
    print(f"✅ DB 초기화 완료: {len(texts)}개 문서")
    
    return True

if __name__ == "__main__":
    success = initialize_db()
    if success:
        print("✅ DB 초기화 성공!")
    else:
        print("❌ DB 초기화 실패")
        sys.exit(1)