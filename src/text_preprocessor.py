#!/usr/bin/env python3
"""
텍스트 전처리 모듈
한국어 텍스트 정규화 및 개선
"""

import re
from typing import List, Dict, Optional, Tuple
import json


class TextPreprocessor:
    def __init__(self):
        # 영어 약어와 한글 설명 매핑
        self.abbreviations = {
            # 부문/조직
            "DX": "디바이스경험부문",
            "DS": "디바이스솔루션부문",
            "MX": "모바일경험",
            "VD": "영상디스플레이",
            
            # 경영/관리
            "CEO": "최고경영자",
            "CFO": "최고재무책임자",
            "CTO": "최고기술책임자",
            "CPO": "최고개인정보보호책임자",
            "CISO": "최고정보보안책임자",
            "ESG": "환경사회거버넌스",
            "CSR": "기업사회책임",
            "CSV": "공유가치창출",
            
            # 환경
            "GHG": "온실가스",
            "CO2": "이산화탄소",
            "CO2e": "이산화탄소환산량",
            "RE100": "재생에너지100",
            "ETS": "배출권거래제",
            "LCA": "전과정평가",
            "PCF": "제품탄소발자국",
            
            # 기술
            "AI": "인공지능",
            "ML": "머신러닝",
            "IoT": "사물인터넷",
            "5G": "5세대이동통신",
            "SW": "소프트웨어",
            "HW": "하드웨어",
            "R&D": "연구개발",
            "IP": "지적재산권",
            
            # 반도체
            "DRAM": "디램",
            "NAND": "낸드플래시",
            "SSD": "솔리드스테이트드라이브",
            "CPU": "중앙처리장치",
            "GPU": "그래픽처리장치",
            "NPU": "신경망처리장치",
            "AP": "애플리케이션프로세서",
            
            # 국제 표준/이니셔티브
            "SDGs": "지속가능발전목표",
            "TCFD": "기후변화재무정보공개",
            "SASB": "지속가능회계기준위원회",
            "GRI": "글로벌보고이니셔티브",
            "CDP": "탄소정보공개프로젝트",
            "UNGC": "유엔글로벌콤팩트",
            "RBA": "책임있는비즈니스연합",
            "RMI": "책임있는광물이니셔티브",
            "AWS": "국제수자원관리동맹",
            
            # 기타
            "M&A": "인수합병",
            "MOU": "업무협약",
            "KPI": "핵심성과지표",
            "CPMS": "컴플라이언스프로그램관리시스템",
            "ERP": "전사적자원관리",
            "SCM": "공급망관리",
        }
        
        # 단위 정규화 매핑
        self.unit_normalizations = {
            "억원": "억 원",
            "조원": "조 원",
            "만원": "만 원",
            "천원": "천 원",
            "만톤": "만 톤",
            "천톤": "천 톤",
            "만명": "만 명",
            "천명": "천 명",
            "퍼센트": "%",
            "프로": "%"
        }
        
        # 중요 키워드 사전
        self.important_keywords = {
            "환경": ["탄소중립", "넷제로", "재생에너지", "자원순환", "수자원", 
                    "생물다양성", "순환경제", "기후변화", "온실가스", "친환경"],
            "사회": ["인권", "안전보건", "다양성", "포용성", "공급망", 
                    "협력회사", "사회공헌", "지역사회", "임직원", "노동"],
            "거버넌스": ["이사회", "지배구조", "준법", "윤리경영", "컴플라이언스",
                      "리스크관리", "투명성", "반부패", "공정거래", "주주"],
            "재무": ["매출", "영업이익", "순이익", "자산", "부채", 
                   "투자", "배당", "실적", "성장", "수익성"],
            "기술": ["혁신", "디지털전환", "반도체", "인공지능", "빅데이터",
                   "클라우드", "보안", "개인정보", "사이버보안", "블록체인"]
        }
    
    def preprocess(self, text: str) -> str:
        """텍스트 전처리 메인 함수"""
        # 1. 기본 정리
        text = self._clean_basic(text)
        
        # 2. 영어 약어 처리
        text = self._process_abbreviations(text)
        
        # 3. 숫자와 단위 정규화
        text = self._normalize_numbers_and_units(text)
        
        # 4. 특수문자 정리
        text = self._clean_special_chars(text)
        
        return text.strip()
    
    def _clean_basic(self, text: str) -> str:
        """기본 텍스트 정리"""
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 연속된 개행을 두 개로
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 탭을 공백으로
        text = text.replace('\t', ' ')
        
        return text
    
    def _process_abbreviations(self, text: str) -> str:
        """영어 약어를 한글 설명과 함께 표기"""
        for abbr, korean in self.abbreviations.items():
            # 이미 병기되어 있는지 확인
            pattern = f"{abbr}\\({korean}\\)"
            if pattern in text:
                continue
            
            # 약어만 있는 경우 한글 병기 추가
            # 단어 경계를 확인하여 정확한 매칭
            text = re.sub(
                rf'\b{re.escape(abbr)}\b(?!\()',
                f'{abbr}({korean})',
                text
            )
        
        return text
    
    def _normalize_numbers_and_units(self, text: str) -> str:
        """숫자와 단위 정규화"""
        # 천단위 구분 쉼표 정규화
        text = re.sub(r'(\d{1,3}),(\d{3})', r'\1,\2', text)
        
        # 단위 정규화
        for old, new in self.unit_normalizations.items():
            text = text.replace(old, new)
        
        # 숫자와 단위 사이 공백 정규화
        # 174조8,877억원 -> 174조 8,877억 원
        text = re.sub(r'(\d+)조(\d+)', r'\1조 \2', text)
        text = re.sub(r'(\d+)억(\d+)', r'\1억 \2', text)
        
        # Scope 1,2,3 정규화
        text = re.sub(r'Scope\s*1', 'Scope 1(직접배출)', text)
        text = re.sub(r'Scope\s*2', 'Scope 2(간접배출)', text)
        text = re.sub(r'Scope\s*3', 'Scope 3(기타간접배출)', text)
        
        return text
    
    def _clean_special_chars(self, text: str) -> str:
        """특수문자 정리"""
        # 이상한 특수문자 제거
        text = re.sub(r'[^\w\s\(\)\[\]\{\}.,;:!?\-=+*/%\'"가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', text)
        
        # 연속된 특수문자 정리
        text = re.sub(r'\.{3,}', '...', text)  # 말줄임표
        text = re.sub(r'-{3,}', '---', text)   # 구분선
        
        return text
    
    def extract_metadata(self, text: str) -> Dict:
        """텍스트에서 메타데이터 추출"""
        metadata = {
            'numbers': self._extract_numbers(text),
            'keywords': self._extract_keywords(text),
            'entities': self._extract_entities(text),
            'dates': self._extract_dates(text)
        }
        
        return metadata
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """중요 수치 추출"""
        numbers = []
        
        # 금액 추출
        money_pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(조|억|만|천)?\s*원'
        for match in re.finditer(money_pattern, text):
            numbers.append({
                'value': match.group(0),
                'type': 'money',
                'unit': '원'
            })
        
        # 퍼센트 추출
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(percent_pattern, text):
            numbers.append({
                'value': match.group(0),
                'type': 'percentage',
                'unit': '%'
            })
        
        # 수량 추출 (톤, 명 등)
        quantity_pattern = r'(\d+(?:,\d{3})*)\s*(톤|명|개|건|회)'
        for match in re.finditer(quantity_pattern, text):
            numbers.append({
                'value': match.group(0),
                'type': 'quantity',
                'unit': match.group(2)
            })
        
        return numbers
    
    def _extract_keywords(self, text: str) -> List[str]:
        """중요 키워드 추출"""
        found_keywords = []
        
        for category, keywords in self.important_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_keywords.append(keyword)
        
        # 중복 제거
        return list(set(found_keywords))
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """개체명 추출 (간단한 규칙 기반)"""
        entities = {
            'organization': [],
            'product': [],
            'location': []
        }
        
        # 조직명
        org_patterns = [
            r'삼성전자(?:주식회사)?',
            r'DX부문|DS부문',
            r'\w+사업부',
            r'\w+센터'
        ]
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            entities['organization'].extend(matches)
        
        # 제품명
        product_patterns = [
            r'갤럭시\s*\w+',
            r'엑시노스\s*\d+',
            r'\w+\s*프로세서'
        ]
        for pattern in product_patterns:
            matches = re.findall(pattern, text)
            entities['product'].extend(matches)
        
        # 지역명
        location_patterns = [
            r'(서울|부산|대구|인천|광주|대전|울산|경기|강원|충북|충남|전북|전남|경북|경남|제주)',
            r'(미국|중국|일본|유럽|아시아|베트남|인도)',
            r'(기흥|화성|평택|천안|온양|구미|광주)(?:사업장|캠퍼스)?'
        ]
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            entities['location'].extend(matches)
        
        # 중복 제거
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_dates(self, text: str) -> List[str]:
        """날짜/연도 추출"""
        dates = []
        
        # 연도
        year_pattern = r'20\d{2}년'
        dates.extend(re.findall(year_pattern, text))
        
        # 날짜
        date_pattern = r'\d{1,2}월\s*\d{1,2}일'
        dates.extend(re.findall(date_pattern, text))
        
        # 분기
        quarter_pattern = r'\d{1}분기|\d{1}Q'
        dates.extend(re.findall(quarter_pattern, text))
        
        return list(set(dates))
    
    def create_search_friendly_text(self, text: str) -> str:
        """검색 최적화된 텍스트 생성"""
        # 전처리
        processed = self.preprocess(text)
        
        # 메타데이터 추출
        metadata = self.extract_metadata(processed)
        
        # 키워드를 텍스트 끝에 추가 (검색 향상)
        if metadata['keywords']:
            keyword_text = ' [키워드: ' + ', '.join(metadata['keywords']) + ']'
            processed += keyword_text
        
        return processed
    
    def normalize_query(self, query: str) -> str:
        """검색 쿼리 정규화"""
        # 기본 전처리
        query = self._clean_basic(query)
        
        # 약어 확장
        for abbr, korean in self.abbreviations.items():
            if abbr.lower() in query.lower():
                query += f" {korean}"
        
        # 동의어 확장
        synonyms = {
            "매출": "매출 수익 실적 영업수익",
            "이익": "이익 영업이익 순이익",
            "환경": "환경 ESG 지속가능 친환경",
            "탄소": "탄소 온실가스 CO2 배출",
            "임직원": "임직원 직원 종업원 근로자"
        }
        
        for key, expansion in synonyms.items():
            if key in query:
                query = expansion
                break
        
        return query.strip()


def test_preprocessor():
    """전처리기 테스트"""
    preprocessor = TextPreprocessor()
    
    # 테스트 텍스트
    test_texts = [
        "DX부문은 2030년까지 Scope 1, 2 탄소중립을 달성할 계획입니다.",
        "2024년 매출은 174조8,877억원을 기록했습니다.",
        "CEO는 ESG 경영의 중요성을 강조했습니다.",
        "재생에너지 전환율이 93.4%에 달했습니다."
    ]
    
    print("📝 텍스트 전처리 테스트:\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"[원본 {i}] {text}")
        processed = preprocessor.preprocess(text)
        print(f"[처리 {i}] {processed}")
        
        metadata = preprocessor.extract_metadata(processed)
        print(f"[메타 {i}] 키워드: {metadata['keywords']}")
        print(f"         수치: {[n['value'] for n in metadata['numbers']]}")
        print()
    
    # 쿼리 정규화 테스트
    print("\n🔍 쿼리 정규화 테스트:\n")
    
    test_queries = [
        "DX 매출",
        "탄소중립 목표",
        "CEO 메시지"
    ]
    
    for query in test_queries:
        normalized = preprocessor.normalize_query(query)
        print(f"[원본] {query}")
        print(f"[정규화] {normalized}\n")


if __name__ == "__main__":
    test_preprocessor()