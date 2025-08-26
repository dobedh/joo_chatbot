#!/usr/bin/env python3
"""
최종 검색 정확도 테스트
구조화된 벡터 DB v3의 성능을 검증
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.korean_vector_store import KoreanVectorStore
from src.hybrid_search import HybridSearch
from src.gemini_rag_pipeline import GeminiRAGPipeline
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def test_vector_search():
    """벡터 검색 테스트"""
    print("=" * 80)
    print("📊 벡터 검색 정확도 테스트")
    print("=" * 80)
    
    # 벡터 스토어 초기화
    vector_store = KoreanVectorStore(
        persist_directory="data/chroma_db"
    )
    
    # 테스트 케이스
    test_cases = [
        {
            "query": "개인정보보호 3대 원칙이 뭐야?",
            "expected": ["투명하게", "안전하게", "사용자의 선택"],
            "description": "구조화된 원칙 검색"
        },
        {
            "query": "미주 2022년 매출 비중은?",
            "expected": ["39%", "39"],
            "description": "표 데이터 검색"
        },
        {
            "query": "HRA가 뭐야?",
            "expected": ["Human Rights", "인권영향평가", "인권"],
            "description": "약어 설명 검색"
        },
        {
            "query": "인권 교육을 몇프로가 받았어?",
            "expected": ["95.7", "95.7%"],
            "description": "수치 데이터 검색"
        },
        {
            "query": "DX부문 2024년 매출은?",
            "expected": ["166.32", "166.32조원"],
            "description": "사업부문 매출 검색"
        },
        {
            "query": "재생에너지 전환율은?",
            "expected": ["33.8", "33.8%"],
            "description": "환경 지표 검색"
        },
        {
            "query": "여성 임직원 비율은?",
            "expected": ["40.7", "40.7%"],
            "description": "사회 지표 검색"
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {test['description']}")
        print(f"질문: {test['query']}")
        
        # 검색 수행
        results = vector_store.similarity_search(test['query'], k=3)
        
        if results:
            # 상위 3개 결과 확인
            found = False
            for j, result in enumerate(results[:3]):
                content = result.page_content
                # 정답 포함 여부 확인
                for expected in test['expected']:
                    if expected.lower() in content.lower():
                        found = True
                        print(f"✅ 정답 발견 (상위 {j+1}번째)")
                        print(f"   찾은 내용: {content[:150]}...")
                        break
                if found:
                    break
            
            if found:
                success_count += 1
            else:
                print(f"❌ 정답 미발견")
                print(f"   상위 결과: {results[0].page_content[:150]}...")
        else:
            print(f"❌ 검색 결과 없음")
    
    # 결과 요약
    print("\n" + "=" * 80)
    print(f"📊 테스트 결과: {success_count}/{len(test_cases)} 성공")
    print(f"🎯 정확도: {success_count/len(test_cases)*100:.1f}%")
    print("=" * 80)
    
    return success_count / len(test_cases)


def test_rag_responses():
    """RAG 응답 테스트"""
    print("\n" + "=" * 80)
    print("🤖 RAG 응답 품질 테스트")
    print("=" * 80)
    
    # RAG 서비스 초기화
    rag_service = GeminiRAGPipeline()
    
    # 테스트 질문
    test_questions = [
        "개인정보보호 3대 원칙에 대해 설명해줘",
        "미주 지역 2022년 매출 비중이 얼마야?",
        "HRA가 뭐야?",
        "인권 교육 이수율이 얼마나 되지?",
        "DX부문 최근 3년간 매출 추이를 알려줘"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n질문 {i}: {question}")
        print("-" * 40)
        
        try:
            # RAG 응답 생성
            response = rag_service.get_response(question)
            print(f"응답: {response['answer'][:300]}...")
            
            if response.get('sources'):
                print(f"참조 소스: {len(response['sources'])}개")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    
    print("\n" + "=" * 80)


def test_hybrid_search():
    """하이브리드 검색 테스트"""
    print("\n" + "=" * 80)
    print("🔄 하이브리드 검색 테스트")
    print("=" * 80)
    
    # 벡터 스토어 초기화
    vector_store = KoreanVectorStore(
        persist_directory="data/chroma_db"
    )
    
    # 하이브리드 검색 초기화
    hybrid_search = HybridSearch(
        vector_store=vector_store,
        dense_weight=0.6
    )
    
    # 테스트 쿼리
    queries = [
        "개인정보보호 원칙",
        "미주 매출",
        "HRA 인권",
        "재생에너지"
    ]
    
    for query in queries:
        print(f"\n쿼리: {query}")
        results = hybrid_search.search(query, k=3)
        
        if results:
            print(f"✅ {len(results)}개 결과 발견")
            print(f"   상위 결과: {results[0].page_content[:100]}...")
        else:
            print("❌ 결과 없음")
    
    print("\n" + "=" * 80)


def main():
    """메인 테스트 실행"""
    print("\n🚀 최종 검색 정확도 테스트 시작\n")
    
    # 1. 벡터 검색 테스트
    accuracy = test_vector_search()
    
    # 2. 하이브리드 검색 테스트
    test_hybrid_search()
    
    # 3. RAG 응답 테스트
    if accuracy > 0.5:  # 정확도가 50% 이상일 때만 RAG 테스트
        test_rag_responses()
    else:
        print("\n⚠️ 벡터 검색 정확도가 낮아 RAG 테스트를 건너뜁니다.")
    
    print("\n✅ 모든 테스트 완료!\n")


if __name__ == "__main__":
    main()