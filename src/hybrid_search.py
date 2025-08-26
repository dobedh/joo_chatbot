#!/usr/bin/env python3
"""
하이브리드 검색 시스템
BM25 (Sparse) + Dense Retrieval 결합
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from langchain.schema import Document
import re
import math


class HybridSearch:
    def __init__(self, vector_store, dense_weight: float = 0.6):
        """
        하이브리드 검색 초기화
        
        Args:
            vector_store: 기존 한국어 벡터 스토어
            dense_weight: Dense 검색 가중치 (0~1)
        """
        self.vector_store = vector_store
        self.dense_weight = dense_weight
        self.sparse_weight = 1 - dense_weight
        
        # BM25 인덱스 구축
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """BM25 인덱스 구축"""
        print("🔄 BM25 인덱스 구축 중...")
        
        # 모든 문서 가져오기
        all_data = self.vector_store.collection.get()
        
        if not all_data or not all_data.get('documents'):
            raise ValueError("벡터 스토어에 문서가 없습니다.")
        
        self.documents = all_data['documents']
        self.metadatas = all_data['metadatas']
        self.ids = all_data['ids']
        
        # 토큰화된 문서 생성
        tokenized_docs = []
        for doc in self.documents:
            tokens = self._tokenize(doc)
            tokenized_docs.append(tokens)
        
        # BM25 인덱스 생성
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f"✅ BM25 인덱스 구축 완료 ({len(self.documents)}개 문서)")
    
    def _tokenize(self, text: str) -> List[str]:
        """간단한 토큰화"""
        # 소문자 변환
        text = text.lower()
        
        # 한글, 영어, 숫자만 추출
        tokens = re.findall(r'[가-힣]+|[a-z]+|[0-9]+\.?[0-9]*%?', text)
        
        # 불용어 제거 (선택적)
        stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로', '와', '과'}
        tokens = [t for t in tokens if t not in stopwords]
        
        return tokens
    
    def search(
        self, 
        query: str, 
        k: int = 5,
        rerank: bool = True
    ) -> List[Document]:
        """
        하이브리드 검색 수행
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
            rerank: 재순위 적용 여부
        
        Returns:
            검색된 문서 리스트
        """
        # 더 많은 후보를 가져와서 재순위
        k_candidates = k * 3 if rerank else k
        
        # Dense 검색 (의미적 유사도)
        dense_results = self._dense_search(query, k_candidates)
        
        # Sparse 검색 (키워드 매칭)
        sparse_results = self._sparse_search(query, k_candidates)
        
        # 결과 통합 및 재순위
        combined_results = self._combine_results(
            dense_results, 
            sparse_results,
            k
        )
        
        return combined_results
    
    def _dense_search(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Dense 검색 (벡터 유사도)"""
        # 기존 벡터 스토어 사용
        docs = self.vector_store.similarity_search(query, k=k)
        
        # 점수와 함께 반환 (거리를 유사도로 변환)
        results = []
        for doc in docs:
            # 거리가 작을수록 유사도가 높음
            distance = doc.metadata.get('distance', 0)
            similarity = 1 / (1 + distance)  # 거리를 유사도로 변환
            results.append((doc, similarity))
        
        return results
    
    def _sparse_search(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Sparse 검색 (BM25)"""
        # 쿼리 토큰화
        query_tokens = self._tokenize(query)
        
        # BM25 점수 계산
        scores = self.bm25.get_scores(query_tokens)
        
        # 상위 k개 선택
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # 점수가 0보다 큰 경우만
                doc = Document(
                    page_content=self.documents[idx],
                    metadata=self.metadatas[idx] if idx < len(self.metadatas) else {}
                )
                # BM25 점수 정규화
                normalized_score = scores[idx] / (scores[idx] + 1)
                results.append((doc, normalized_score))
        
        return results
    
    def _combine_results(
        self, 
        dense_results: List[Tuple[Document, float]],
        sparse_results: List[Tuple[Document, float]],
        k: int
    ) -> List[Document]:
        """Dense와 Sparse 결과 통합"""
        # 문서별 점수 집계
        doc_scores = {}
        
        # Dense 결과 처리
        for doc, score in dense_results:
            key = doc.page_content[:100]  # 문서 식별 키
            if key not in doc_scores:
                doc_scores[key] = {
                    'doc': doc,
                    'dense_score': 0,
                    'sparse_score': 0
                }
            doc_scores[key]['dense_score'] = score
        
        # Sparse 결과 처리
        for doc, score in sparse_results:
            key = doc.page_content[:100]
            if key not in doc_scores:
                doc_scores[key] = {
                    'doc': doc,
                    'dense_score': 0,
                    'sparse_score': 0
                }
            doc_scores[key]['sparse_score'] = score
        
        # 최종 점수 계산
        final_scores = []
        for key, scores in doc_scores.items():
            combined_score = (
                self.dense_weight * scores['dense_score'] +
                self.sparse_weight * scores['sparse_score']
            )
            final_scores.append((scores['doc'], combined_score))
        
        # 점수 기준 정렬
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 k개 반환
        return [doc for doc, _ in final_scores[:k]]
    
    def search_with_filter(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """필터를 적용한 하이브리드 검색"""
        # 기본 검색
        all_results = self.search(query, k=k*2)  # 더 많이 가져온 후 필터링
        
        if not filter_dict:
            return all_results[:k]
        
        # 필터 적용
        filtered = []
        for doc in all_results:
            match = True
            for key, value in filter_dict.items():
                if doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(doc)
        
        return filtered[:k]


def test_hybrid_search():
    """하이브리드 검색 테스트"""
    from pathlib import Path
    from korean_vector_store import KoreanVectorStore
    
    print("=" * 70)
    print("🔍 하이브리드 검색 테스트")
    print("=" * 70)
    
    # 벡터 스토어 로드
    korean_db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    vector_store = KoreanVectorStore(persist_directory=str(korean_db_path))
    
    # 하이브리드 검색 초기화
    hybrid = HybridSearch(vector_store, dense_weight=0.6)
    
    # 테스트 쿼리
    test_queries = [
        "인권 교육을 몇프로가 받았어?",
        "HRA",
        "인권 챔피언",
        "DX부문 탄소중립"
    ]
    
    for query in test_queries:
        print(f"\n📝 쿼리: '{query}'")
        print("-" * 50)
        
        results = hybrid.search(query, k=3)
        
        for i, doc in enumerate(results, 1):
            page = doc.metadata.get('page', 'N/A')
            section = doc.metadata.get('section', 'N/A')
            
            # 주요 키워드 확인
            content = doc.page_content
            highlights = []
            
            if '95.7%' in content:
                highlights.append('95.7%')
            if 'HRA' in content or 'Human Rights Risk Assessment' in content:
                highlights.append('HRA')
            if '인권 챔피언' in content:
                highlights.append('인권 챔피언')
            
            print(f"\n[{i}] 페이지 {page}, 섹션: {section}")
            if highlights:
                print(f"✅ 포함: {', '.join(highlights)}")
            print(f"내용: {content[:150]}...")
    
    print("\n" + "=" * 70)
    print("✅ 하이브리드 검색 테스트 완료")


if __name__ == "__main__":
    test_hybrid_search()