#!/usr/bin/env python3
"""
스마트 청킹 모듈
의미 단위로 텍스트를 분할하고 메타데이터를 추출
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path


class SmartChunker:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 300):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 주요 섹션 키워드
        self.section_keywords = {
            'DX부문': ['DX', 'Device eXperience', '모바일', 'TV', '가전'],
            'DS부문': ['DS', 'Device Solutions', '반도체', '메모리', 'Foundry'],
            '환경': ['환경', '기후변화', '탄소중립', '재생에너지', '자원순환', '수자원'],
            '사회': ['임직원', '공급망', '사회공헌', '인권', '안전보건'],
            '거버넌스': ['이사회', '지배구조', '준법', '윤리경영', '컴플라이언스']
        }
        
        # 중요 수치 패턴
        self.number_patterns = [
            r'\d+조\s*\d*[천백십억만]*원',  # 조 단위 금액
            r'\d+억\s*\d*[천백십만]*원',    # 억 단위 금액
            r'\d+\.?\d*%',                 # 퍼센트
            r'\d{4}년',                    # 연도
            r'\d+만\s*톤',                 # 톤 단위
            r'\d+[천백십만]*명',            # 인원수
        ]
    
    def chunk_markdown(self, markdown_path: Path) -> List[Dict]:
        """마크다운 파일을 청킹"""
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = []
        
        # 페이지별로 분할
        pages = self._split_by_pages(content)
        
        for page_num, page_content in pages:
            # 각 페이지를 섹션별로 분할
            page_chunks = self._chunk_page(page_content, page_num)
            chunks.extend(page_chunks)
        
        return chunks
    
    def _split_by_pages(self, content: str) -> List[Tuple[int, str]]:
        """페이지별로 분할"""
        pages = []
        
        # 페이지 구분자로 분할
        page_splits = re.split(r'## 페이지 (\d+)', content)
        
        # 첫 번째 요소는 헤더이므로 제외
        for i in range(1, len(page_splits), 2):
            if i + 1 < len(page_splits):
                page_num = int(page_splits[i])
                page_content = page_splits[i + 1]
                pages.append((page_num, page_content))
        
        return pages
    
    def _chunk_page(self, page_content: str, page_num: int) -> List[Dict]:
        """페이지 내용을 청킹"""
        chunks = []
        
        # 표 데이터 섹션 찾기
        table_sections = re.findall(
            r'### 📊 주요 데이터\n```(.*?)```', 
            page_content, 
            re.DOTALL
        )
        
        # 표 데이터는 통째로 하나의 청크로
        for table in table_sections:
            if table.strip():
                chunk_data = {
                    'content': table.strip(),
                    'metadata': {
                        'page': page_num,
                        'chunk_type': 'table',
                        'section': self._detect_section(page_content),
                        'metrics': self._extract_numbers(table),
                        'keywords': self._extract_keywords(table)
                    }
                }
                chunks.append(chunk_data)
        
        # 표를 제외한 나머지 텍스트 처리
        text_without_tables = re.sub(
            r'### 📊 주요 데이터\n```.*?```', 
            '', 
            page_content, 
            flags=re.DOTALL
        )
        
        # 섹션별로 분할 (### 기준)
        sections = re.split(r'###\s+', text_without_tables)
        
        for section in sections:
            if not section.strip():
                continue
            
            # 섹션 제목과 내용 분리
            lines = section.split('\n', 1)
            section_title = lines[0].strip() if lines else ''
            section_content = lines[1] if len(lines) > 1 else section
            
            # 섹션 내용을 청크로 분할
            if section_content.strip():
                section_chunks = self._create_chunks_from_text(
                    section_content,
                    page_num,
                    section_title
                )
                chunks.extend(section_chunks)
        
        return chunks
    
    def _create_chunks_from_text(
        self, 
        text: str, 
        page_num: int,
        section_title: str = ''
    ) -> List[Dict]:
        """텍스트를 청크로 분할"""
        chunks = []
        
        # 문단별로 분리
        paragraphs = re.split(r'\n\n+', text)
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # 현재 청크에 추가할지 결정
            if current_length + para_length <= self.chunk_size:
                current_chunk.append(para)
                current_length += para_length
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(self._create_chunk_data(
                        chunk_text, 
                        page_num, 
                        section_title
                    ))
                
                # 새 청크 시작
                current_chunk = [para]
                current_length = para_length
        
        # 마지막 청크 저장
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(self._create_chunk_data(
                chunk_text, 
                page_num, 
                section_title
            ))
        
        return chunks
    
    def _create_chunk_data(
        self, 
        text: str, 
        page_num: int,
        section_title: str = ''
    ) -> Dict:
        """청크 데이터 생성"""
        # 섹션 감지
        section = self._detect_section(text)
        
        # 청크 타입 결정
        chunk_type = self._detect_chunk_type(text)
        
        # 메타데이터 생성
        metadata = {
            'page': page_num,
            'section': section,
            'subsection': section_title,
            'chunk_type': chunk_type,
            'metrics': self._extract_numbers(text),
            'keywords': self._extract_keywords(text),
            'char_count': len(text)
        }
        
        # 연도 정보 추출
        years = re.findall(r'(20\d{2})년', text)
        if years:
            metadata['years'] = list(set(years))
        
        return {
            'content': text,
            'metadata': metadata
        }
    
    def _detect_section(self, text: str) -> str:
        """텍스트가 속한 섹션 감지"""
        text_lower = text.lower()
        
        for section, keywords in self.section_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return section
        
        return '일반'
    
    def _detect_chunk_type(self, text: str) -> str:
        """청크 타입 감지"""
        # CEO 메시지 감지
        if 'CEO 메시지' in text or '대표이사' in text:
            return 'ceo_message'
        
        # 제목/헤더 감지 (짧고 개행이 없음)
        if len(text) < 100 and '\n' not in text:
            return 'header'
        
        # 리스트 감지
        if text.count('•') > 2 or text.count('·') > 2:
            return 'list'
        
        # 숫자가 많으면 데이터
        numbers = re.findall(r'\d+[조억만천백십]?\s*[원톤명개%]', text)
        if len(numbers) > 3:
            return 'data'
        
        return 'text'
    
    def _extract_numbers(self, text: str) -> List[str]:
        """중요 수치 추출"""
        numbers = []
        
        for pattern in self.number_patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)
        
        # 중복 제거 및 정렬
        return list(set(numbers))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """핵심 키워드 추출"""
        keywords = []
        
        # 정의된 중요 키워드 (확장)
        important_terms = [
            '탄소중립', '재생에너지', 'ESG', '지속가능', 
            '매출', '영업이익', '환경', '안전', '인권',
            'AI', '반도체', '혁신', '디지털', '그린',
            '순환경제', '생물다양성', '넷제로',
            # 추가 키워드
            'HRA', 'Human Rights Risk Assessment', '인권 리스크 평가',
            '인권 챔피언', '인권 교육', '수료율', '95.7%',
            'DX부문', 'DS부문', 'Scope 1', 'Scope 2', 'Scope 3',
            'TCFD', 'SASB', 'GRI', 'CDP', 'UNGC', 'RBA',
            '온실가스', 'CO2', '배출량', '재활용', '폐기물'
        ]
        
        # 영어 약어 패턴 추출 (대문자 2글자 이상)
        import re
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.extend(acronyms)
        
        for term in important_terms:
            if term in text:
                keywords.append(term)
        
        # 중복 제거
        return list(set(keywords))
    
    def create_overlap_chunks(
        self, 
        text: str, 
        chunk_size: int = 500,
        overlap: int = 100
    ) -> List[str]:
        """오버랩이 있는 청크 생성"""
        chunks = []
        
        # 문장 단위로 분리
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size <= chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # 오버랩 처리 - 마지막 몇 문장을 다음 청크에 포함
                overlap_sentences = []
                overlap_size = 0
                
                for sent in reversed(current_chunk):
                    if overlap_size + len(sent) <= overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_size += len(sent)
                    else:
                        break
                
                # 새 청크 시작 (오버랩 포함)
                current_chunk = overlap_sentences + [sentence]
                current_size = overlap_size + sentence_size
        
        # 마지막 청크
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


def test_chunker():
    """청커 테스트"""
    markdown_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_advanced.md")
    
    if not markdown_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {markdown_path}")
        return
    
    chunker = SmartChunker(chunk_size=1200, chunk_overlap=300)
    chunks = chunker.chunk_markdown(markdown_path)
    
    print(f"📊 청킹 결과:")
    print(f"  총 청크 수: {len(chunks)}")
    
    # 청크 타입별 통계
    chunk_types = {}
    sections = {}
    
    for chunk in chunks:
        chunk_type = chunk['metadata'].get('chunk_type', 'unknown')
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        section = chunk['metadata'].get('section', 'unknown')
        sections[section] = sections.get(section, 0) + 1
    
    print(f"\n📈 청크 타입 분포:")
    for ctype, count in sorted(chunk_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ctype}: {count}개")
    
    print(f"\n📑 섹션별 분포:")
    for section, count in sorted(sections.items(), key=lambda x: x[1], reverse=True):
        print(f"  {section}: {count}개")
    
    # 샘플 출력
    print(f"\n📝 샘플 청크 (처음 3개):")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n[청크 {i+1}]")
        print(f"  페이지: {chunk['metadata']['page']}")
        print(f"  섹션: {chunk['metadata']['section']}")
        print(f"  타입: {chunk['metadata']['chunk_type']}")
        print(f"  내용: {chunk['content'][:100]}...")
        if chunk['metadata'].get('metrics'):
            print(f"  수치: {chunk['metadata']['metrics'][:3]}")


if __name__ == "__main__":
    test_chunker()