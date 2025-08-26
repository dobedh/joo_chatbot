#!/usr/bin/env python3
"""
한국어 최적화 벡터 DB 구축 스크립트
ko-sroberta 모델과 스마트 청킹을 사용한 고품질 임베딩
"""

import os
import sys
from pathlib import Path
import shutil
import time
from typing import List, Dict

# 모듈 임포트
from korean_vector_store import KoreanVectorStore
from smart_chunker import SmartChunker
from text_preprocessor import TextPreprocessor


def build_korean_vectordb():
    """한국어 최적화 벡터 DB 구축"""
    
    print("=" * 60)
    print("🚀 한국어 최적화 벡터 DB 구축 시작")
    print("=" * 60)
    
    # 경로 설정
    markdown_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_advanced.md")
    db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    
    # 파일 확인
    if not markdown_path.exists():
        print(f"❌ 마크다운 파일을 찾을 수 없습니다: {markdown_path}")
        return False
    
    print(f"📄 입력 파일: {markdown_path}")
    print(f"💾 출력 경로: {db_path}")
    
    # 기존 DB 삭제
    if db_path.exists():
        print("\n🗑️ 기존 벡터 DB 삭제 중...")
        shutil.rmtree(db_path)
        print("✅ 기존 DB 삭제 완료")
    
    # 1단계: 청킹
    print("\n" + "=" * 60)
    print("📝 1단계: 스마트 청킹")
    print("-" * 60)
    
    start_time = time.time()
    chunker = SmartChunker(chunk_size=1200, chunk_overlap=300)
    chunks = chunker.chunk_markdown(markdown_path)
    
    print(f"✅ {len(chunks)}개 청크 생성 완료")
    print(f"⏱️ 소요 시간: {time.time() - start_time:.2f}초")
    
    # 청크 통계
    print_chunk_statistics(chunks)
    
    # 2단계: 텍스트 전처리
    print("\n" + "=" * 60)
    print("🔧 2단계: 텍스트 전처리")
    print("-" * 60)
    
    start_time = time.time()
    preprocessor = TextPreprocessor()
    
    processed_chunks = []
    for chunk in chunks:
        # 텍스트 전처리
        processed_text = preprocessor.preprocess(chunk['content'])
        
        # 메타데이터 보강 (ChromaDB는 리스트를 지원하지 않으므로 문자열로 변환)
        extracted_metadata = preprocessor.extract_metadata(processed_text)
        
        # 리스트를 문자열로 변환
        metadata = chunk['metadata'].copy()
        
        # 기존 리스트 필드 처리
        if 'metrics' in metadata and isinstance(metadata['metrics'], list):
            metadata['metrics'] = ', '.join(metadata['metrics']) if metadata['metrics'] else ''
        if 'keywords' in metadata and isinstance(metadata['keywords'], list):
            metadata['keywords'] = ', '.join(metadata['keywords']) if metadata['keywords'] else ''
        if 'years' in metadata and isinstance(metadata['years'], list):
            metadata['years'] = ', '.join(metadata['years']) if metadata['years'] else ''
        
        # 추출된 메타데이터 추가
        metadata['extracted_keywords'] = ', '.join(extracted_metadata['keywords']) if extracted_metadata['keywords'] else ''
        metadata['extracted_numbers'] = ', '.join([n['value'] for n in extracted_metadata['numbers']]) if extracted_metadata['numbers'] else ''
        metadata['extracted_dates'] = ', '.join(extracted_metadata['dates']) if extracted_metadata['dates'] else ''
        
        processed_chunks.append({
            'content': processed_text,
            'metadata': metadata
        })
    
    print(f"✅ {len(processed_chunks)}개 청크 전처리 완료")
    print(f"⏱️ 소요 시간: {time.time() - start_time:.2f}초")
    
    # 3단계: 벡터 DB 구축
    print("\n" + "=" * 60)
    print("🗄️ 3단계: 벡터 DB 구축 (ko-sroberta)")
    print("-" * 60)
    
    start_time = time.time()
    
    # 벡터 스토어 초기화
    vector_store = KoreanVectorStore(persist_directory=str(db_path))
    
    # 텍스트와 메타데이터 분리
    texts = [chunk['content'] for chunk in processed_chunks]
    metadatas = [chunk['metadata'] for chunk in processed_chunks]
    
    # 벡터 DB에 추가
    vector_store.add_documents(texts, metadatas)
    
    print(f"⏱️ 소요 시간: {time.time() - start_time:.2f}초")
    
    # 4단계: 검증
    print("\n" + "=" * 60)
    print("🔍 4단계: 벡터 DB 검증")
    print("-" * 60)
    
    # DB 통계
    stats = vector_store.get_statistics()
    print(f"\n📊 벡터 DB 통계:")
    print(f"  총 문서 수: {stats['total_documents']}")
    print(f"  고유 페이지: {stats['unique_pages']}")
    print(f"  고유 섹션: {stats['unique_sections']}")
    print(f"  임베딩 차원: {stats['embedding_dimension']}")
    
    if stats.get('chunk_types'):
        print(f"\n  청크 타입 분포:")
        for ctype, count in stats['chunk_types'].items():
            print(f"    {ctype}: {count}개")
    
    # 테스트 검색
    print("\n" + "=" * 60)
    print("🧪 테스트 검색")
    print("-" * 60)
    
    test_queries = [
        "2024년 매출 실적",
        "DX부문 탄소중립 목표",
        "재생에너지 전환율",
        "CEO 메시지",
        "DS부문 반도체 사업",
        "ESG 전략",
        "협력회사 지원",
        "임직원 복지"
    ]
    
    for query in test_queries:
        print(f"\n🔎 검색: '{query}'")
        results = vector_store.similarity_search(query, k=3)
        
        if results:
            for i, doc in enumerate(results, 1):
                print(f"\n  [{i}] 페이지 {doc.metadata.get('page', 'N/A')}, "
                      f"섹션: {doc.metadata.get('section', 'N/A')}")
                print(f"      {doc.page_content[:150]}...")
                
                # 수치 정보가 있으면 표시
                if doc.metadata.get('metrics'):
                    print(f"      📊 수치: {', '.join(doc.metadata['metrics'][:3])}")
        else:
            print("  ❌ 검색 결과 없음")
    
    print("\n" + "=" * 60)
    print("✅ 한국어 최적화 벡터 DB 구축 완료!")
    print(f"📁 저장 위치: {db_path}")
    print("=" * 60)
    
    return True


def print_chunk_statistics(chunks: List[Dict]):
    """청크 통계 출력"""
    # 타입별 통계
    type_stats = {}
    section_stats = {}
    page_stats = {}
    
    total_chars = 0
    metrics_count = 0
    keywords_count = 0
    
    for chunk in chunks:
        metadata = chunk['metadata']
        
        # 타입 통계
        chunk_type = metadata.get('chunk_type', 'unknown')
        type_stats[chunk_type] = type_stats.get(chunk_type, 0) + 1
        
        # 섹션 통계
        section = metadata.get('section', 'unknown')
        section_stats[section] = section_stats.get(section, 0) + 1
        
        # 페이지 통계
        page = metadata.get('page', 0)
        if page not in page_stats:
            page_stats[page] = 0
        page_stats[page] += 1
        
        # 문자 수
        total_chars += len(chunk['content'])
        
        # 메트릭과 키워드
        if metadata.get('metrics'):
            metrics_count += len(metadata['metrics'])
        if metadata.get('keywords'):
            keywords_count += len(metadata['keywords'])
    
    print(f"\n📈 청크 통계:")
    print(f"  평균 청크 크기: {total_chars // len(chunks)}자")
    print(f"  총 수치 정보: {metrics_count}개")
    print(f"  총 키워드: {keywords_count}개")
    
    print(f"\n  타입별 분포:")
    for ctype, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / len(chunks)) * 100
        print(f"    {ctype}: {count}개 ({percentage:.1f}%)")
    
    print(f"\n  섹션별 분포:")
    for section, count in sorted(section_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / len(chunks)) * 100
        print(f"    {section}: {count}개 ({percentage:.1f}%)")
    
    print(f"\n  페이지 범위: {min(page_stats.keys())} ~ {max(page_stats.keys())}")


if __name__ == "__main__":
    # 필요한 패키지 확인
    try:
        import torch
        import transformers
        import chromadb
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("\n다음 명령어로 설치하세요:")
        print("pip install torch transformers chromadb")
        sys.exit(1)
    
    # 실행
    success = build_korean_vectordb()
    
    if success:
        print("\n💡 다음 단계:")
        print("1. app_gemini.py를 수정하여 새 벡터 DB 사용")
        print("2. korean_vector_store.py를 import하도록 변경")
        print("3. 챗봇을 실행하여 개선된 검색 성능 테스트")
    
    sys.exit(0 if success else 1)