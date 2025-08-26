#!/usr/bin/env python3
"""
한국어 특화 벡터 스토어
ko-sroberta-multitask 모델을 사용한 한국어 임베딩 최적화
"""

from typing import List, Dict, Optional

# SQLite 버전 패치 for Streamlit Cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass  # Local environment doesn't need this patch

import chromadb
from chromadb.config import Settings
from langchain.schema import Document
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
import os

class KoreanVectorStore:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        
        # ko-sroberta-multitask 모델 로드
        print("🔄 한국어 임베딩 모델 로딩 중...")
        self.tokenizer = AutoTokenizer.from_pretrained("jhgan/ko-sroberta-multitask")
        self.model = AutoModel.from_pretrained("jhgan/ko-sroberta-multitask")
        self.model.eval()  # 평가 모드로 설정
        
        # ChromaDB 클라이언트 초기화
        self.client = None
        self.collection = None
        self._initialize_store()
        
        # 영어 약어 매핑 테이블
        self.abbreviation_map = {
            "DX": "DX(디바이스경험부문)",
            "DS": "DS(디바이스솔루션부문)",
            "CEO": "CEO(최고경영자)",
            "ESG": "ESG(환경사회거버넌스)",
            "SDGs": "SDGs(지속가능발전목표)",
            "AWS": "AWS(국제수자원관리동맹)",
            "TCFD": "TCFD(기후변화재무정보공개)",
            "CPMS": "CPMS(컴플라이언스프로그램관리시스템)",
            "RBA": "RBA(책임있는비즈니스연합)",
            "Scope 1": "Scope 1(직접배출)",
            "Scope 2": "Scope 2(간접배출)",
            "Scope 3": "Scope 3(기타간접배출)",
            "AI": "AI(인공지능)",
            "SW": "SW(소프트웨어)",
            "R&D": "R&D(연구개발)",
            "M&A": "M&A(인수합병)",
            "NPU": "NPU(신경망처리장치)",
            "GPU": "GPU(그래픽처리장치)",
            "CPU": "CPU(중앙처리장치)"
        }
        
        # 동의어 매핑
        self.synonym_map = {
            "매출": ["매출", "수익", "실적", "매출액", "영업수익"],
            "이익": ["이익", "영업이익", "순이익", "수익성"],
            "환경": ["환경", "친환경", "지속가능", "ESG", "그린"],
            "탄소": ["탄소", "온실가스", "CO2", "이산화탄소", "배출량"],
            "재생에너지": ["재생에너지", "신재생에너지", "재생가능에너지", "태양광", "풍력"],
            "폐기물": ["폐기물", "쓰레기", "폐제품", "재활용", "순환자원"],
            "임직원": ["임직원", "직원", "종업원", "근로자", "인력"],
            "협력사": ["협력사", "협력회사", "공급업체", "파트너사", "벤더"]
        }
    
    def _initialize_store(self):
        """ChromaDB 컬렉션 초기화"""
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # 기존 컬렉션이 있는지 확인
        try:
            self.collection = self.client.get_collection("samsung_esg_korean")
            doc_count = self.collection.count()
            if doc_count > 0:
                print(f"✅ 기존 ChromaDB 컬렉션 로드 완료 ({doc_count}개 문서)")
            else:
                print("⚠️ 빈 컬렉션이 감지되었습니다.")
        except:
            # 컬렉션이 없으면 새로 생성
            self.collection = self.client.create_collection(
                name="samsung_esg_korean",
                metadata={"description": "삼성전자 ESG 보고서 - 한국어 최적화"}
            )
            print("✅ 새 ChromaDB 컬렉션 생성 완료")
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리 - 영어 약어를 한글 병기로 변환"""
        # 영어 약어 처리
        for eng, kor in self.abbreviation_map.items():
            # 이미 병기되어 있지 않은 경우만 변환
            if eng in text and kor not in text:
                text = text.replace(eng, kor)
        
        return text
    
    def enhance_query(self, query: str) -> str:
        """검색 쿼리 확장 - 동의어 추가"""
        enhanced = query
        
        # 동의어 확장
        for key, synonyms in self.synonym_map.items():
            if key in query:
                # 동의어를 추가 (중복 제거)
                for synonym in synonyms:
                    if synonym not in enhanced:
                        enhanced += f" {synonym}"
        
        return enhanced
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """ko-sroberta를 사용한 텍스트 임베딩"""
        # 텍스트 전처리
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # 토크나이징
        inputs = self.tokenizer(
            processed_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # 임베딩 생성
        with torch.no_grad():
            outputs = self.model(**inputs)
            # [CLS] 토큰의 hidden state를 사용
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return embeddings
    
    def add_documents(self, texts: List[str], metadatas: List[Dict]):
        """문서를 벡터 DB에 추가"""
        if not texts:
            return
        
        print(f"📝 {len(texts)}개 문서를 벡터 DB에 추가 중...")
        
        # ID 생성
        ids = [f"doc_{i:04d}" for i in range(len(texts))]
        
        # 배치 처리 (메모리 효율성)
        batch_size = 50  # ko-sroberta는 무거우므로 배치 크기 축소
        
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_metadata = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]
            
            # 임베딩 생성
            print(f"  배치 {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} 임베딩 생성 중...")
            embeddings = self.get_embeddings(batch_texts)
            
            # ChromaDB에 추가
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=batch_texts,
                metadatas=batch_metadata,
                ids=batch_ids
            )
        
        # ChromaDB PersistentClient는 자동으로 저장되므로 별도 persist 불필요
        print(f"✅ 벡터 DB 저장 완료: {self.persist_directory}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """유사도 검색"""
        
        # 쿼리 확장
        enhanced_query = self.enhance_query(query)
        
        # 쿼리 임베딩
        query_embedding = self.get_embeddings([enhanced_query])[0]
        
        # 검색 실행
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            where=filter  # 메타데이터 필터링
        )
        
        # Document 객체로 변환
        documents = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata, distance in zip(
                results['documents'][0], 
                results['metadatas'][0],
                results['distances'][0] if 'distances' in results else [0] * len(results['documents'][0])
            ):
                metadata['distance'] = distance  # 거리 정보 추가
                documents.append(Document(
                    page_content=doc,
                    metadata=metadata
                ))
        
        return documents
    
    def search_with_context(self, query: str, k: int = 5) -> List[Document]:
        """컨텍스트를 포함한 검색 (앞뒤 청크 포함)"""
        # 기본 검색
        docs = self.similarity_search(query, k=k)
        
        # 각 문서의 앞뒤 청크도 가져오기
        extended_docs = []
        added_ids = set()
        
        for doc in docs:
            chunk_id = doc.metadata.get('chunk_id', '')
            if chunk_id and chunk_id not in added_ids:
                # 현재 청크
                extended_docs.append(doc)
                added_ids.add(chunk_id)
                
                # TODO: 앞뒤 청크 가져오기 로직 구현
                # 이는 chunk_id 체계에 따라 구현 필요
        
        return extended_docs
    
    def exists(self) -> bool:
        """벡터 스토어에 데이터가 있는지 확인"""
        try:
            count = self.collection.count()
            return count > 0
        except:
            return False
    
    def clear(self):
        """벡터 스토어 초기화"""
        if self.collection:
            # 모든 문서 삭제
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
            print("🗑️ 벡터 스토어 초기화 완료")
    
    def get_statistics(self) -> Dict:
        """벡터 DB 통계 정보"""
        if not self.collection:
            return {}
        
        data = self.collection.get()
        
        # 메타데이터 분석
        sections = set()
        pages = set()
        chunk_types = {}
        
        for metadata in data.get('metadatas', []):
            if 'section' in metadata:
                sections.add(metadata['section'])
            if 'page' in metadata:
                pages.add(metadata['page'])
            if 'chunk_type' in metadata:
                chunk_type = metadata['chunk_type']
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        return {
            'total_documents': len(data.get('ids', [])),
            'unique_sections': len(sections),
            'unique_pages': len(pages),
            'chunk_types': chunk_types,
            'embedding_dimension': 768  # ko-sroberta dimension
        }


# VectorStore 클래스 (기존 인터페이스와 호환)
class VectorStore(KoreanVectorStore):
    """기존 코드와의 호환성을 위한 래퍼 클래스"""
    
    def add_documents(self, texts: List[str], metadatas: List[Dict] = None):
        """기존 인터페이스 유지"""
        if metadatas is None:
            metadatas = [{}] * len(texts)
        super().add_documents(texts, metadatas)