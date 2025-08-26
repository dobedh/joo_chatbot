#!/usr/bin/env python3
"""
벡터 DB 구축 스크립트
"""

from pathlib import Path
from gemini_vector_store import VectorStore
import re
from typing import List, Dict


def create_chunks(markdown_path: Path) -> List[Dict]:
    """마크다운을 청크로 분할"""
    
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = []
    
    # 페이지 단위로 분할
    pages = content.split('## 페이지')
    
    for page_content in pages[1:]:  # 첫 번째는 헤더
        # 페이지 번호 추출
        page_match = re.match(r' (\d+)', page_content)
        if not page_match:
            continue
        
        page_num = page_match.group(1)
        
        # 내용을 더 작은 청크로 분할 (600자 단위 - 더 많은 컨텍스트)
        text = page_content[page_match.end():]
        chunk_size = 600
        
        # 섹션별로 분리 (### 기준)
        sections = text.split('###')
        
        for section in sections:
            if not section.strip():
                continue
                
            # 섹션이 너무 길면 청크로 분할
            if len(section) > chunk_size:
                for i in range(0, len(section), chunk_size):
                    chunk_text = section[i:i+chunk_size].strip()
                    
                    if len(chunk_text) > 50:  # 의미 있는 내용만
                        chunks.append({
                            'content': chunk_text,
                            'metadata': {
                                'page': int(page_num),
                                'chunk_start': i,
                                'chunk_end': min(i+chunk_size, len(section)),
                                'source': 'samsung_esg_advanced.md'
                            }
                        })
            else:
                # 섹션이 적당한 크기면 그대로 사용
                if len(section.strip()) > 50:
                    chunks.append({
                        'content': section.strip(),
                        'metadata': {
                            'page': int(page_num),
                            'chunk_start': 0,
                            'chunk_end': len(section),
                            'source': 'samsung_esg_advanced.md'
                        }
                    })
    
    return chunks


def main():
    # 경로 설정
    markdown_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_advanced.md")
    db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db")
    
    # 기존 DB 삭제
    if db_path.exists():
        import shutil
        shutil.rmtree(db_path)
        print("🗑️ 기존 벡터 DB 삭제 완료")
    
    # 청크 생성
    print("📝 청크 생성 중...")
    chunks = create_chunks(markdown_path)
    print(f"✅ {len(chunks)}개 청크 생성 완료")
    
    # 벡터 스토어 초기화
    print("🚀 벡터 DB 구축 중...")
    vector_store = VectorStore(persist_directory=str(db_path))
    
    # 문서 추가
    texts = [chunk['content'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    
    vector_store.add_documents(texts, metadatas)
    print(f"✅ 벡터 DB 구축 완료: {db_path}")
    
    # 샘플 검색 테스트
    print("\n🔍 검색 테스트...")
    test_queries = [
        "삼성전자 매출 영업이익",
        "탄소중립 목표",
        "재생에너지 전환율",
        "CEO 메시지",
        "DS부문 실적"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = vector_store.similarity_search(query, k=2)
        for i, doc in enumerate(results):
            print(f"  결과 {i+1} (페이지 {doc.metadata.get('page', 'N/A')}):")
            print(f"    {doc.page_content[:100]}...")
    
    return db_path


if __name__ == "__main__":
    db_path = main()
    print(f"\n🎯 완료! 벡터 DB 위치: {db_path}")