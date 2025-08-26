#!/usr/bin/env python3
"""
PyMuPDF와 Gemini를 사용한 고급 PDF 추출기
표와 텍스트를 정확하게 추출하고 정제
"""

import fitz  # PyMuPDF
from pathlib import Path
import re
import json
from typing import List, Dict, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class AdvancedPDFExtractor:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.doc = None
        self.extracted_content = []
        
        # Gemini 설정
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def extract(self) -> List[Dict]:
        """PDF 전체 추출"""
        print(f"📚 고급 PDF 추출 시작: {self.pdf_path}")
        
        self.doc = fitz.open(self.pdf_path)
        total_pages = len(self.doc)
        
        for page_num in range(total_pages):
            print(f"처리 중: 페이지 {page_num + 1}/{total_pages}")
            page = self.doc[page_num]
            
            page_content = self._extract_page(page, page_num + 1)
            if page_content:
                self.extracted_content.append(page_content)
        
        self.doc.close()
        return self.extracted_content
    
    def _extract_page(self, page, page_num: int) -> Dict:
        """각 페이지 추출 및 구조화"""
        page_data = {
            'page': page_num,
            'text': '',
            'tables': [],
            'structured_content': ''
        }
        
        # 1. 텍스트 추출
        text = page.get_text()
        page_data['text'] = self._clean_text(text)
        
        # 2. 표 추출 시도
        tables = self._extract_tables_from_page(page)
        if tables:
            page_data['tables'] = tables
        
        # 3. 구조화된 컨텐츠 생성
        page_data['structured_content'] = self._create_structured_content(
            page_data['text'], 
            page_data['tables'],
            page_num
        )
        
        return page_data
    
    def _extract_tables_from_page(self, page) -> List[Dict]:
        """페이지에서 표 추출"""
        tables = []
        
        # PyMuPDF의 표 감지 기능 사용
        try:
            # 텍스트 블록 분석
            blocks = page.get_text("dict")
            
            # 테이블 패턴 감지 (숫자와 구분자가 많은 영역)
            potential_tables = self._detect_table_regions(blocks)
            
            for table_region in potential_tables:
                table_data = self._parse_table_region(table_region)
                if table_data:
                    tables.append(table_data)
        except Exception as e:
            print(f"표 추출 오류: {e}")
        
        return tables
    
    def _detect_table_regions(self, blocks) -> List:
        """표 영역 감지"""
        table_regions = []
        
        for block in blocks.get('blocks', []):
            if block.get('type') == 0:  # 텍스트 블록
                lines = block.get('lines', [])
                
                # 숫자가 많고 정렬된 패턴 찾기
                numeric_lines = 0
                for line in lines:
                    text = ''.join([span['text'] for span in line.get('spans', [])])
                    # 숫자, 콤마, 조, 억, 원 등이 포함된 라인
                    if re.search(r'\d+[,\d]*\s*(조|억|원|%|개)', text):
                        numeric_lines += 1
                
                # 숫자가 많은 블록은 표일 가능성이 높음
                if numeric_lines >= 2:
                    table_regions.append(block)
        
        return table_regions
    
    def _parse_table_region(self, region) -> Optional[Dict]:
        """표 영역 파싱"""
        lines = []
        for line in region.get('lines', []):
            text = ''.join([span['text'] for span in line.get('spans', [])])
            lines.append(text.strip())
        
        if not lines:
            return None
        
        # 표를 구조화된 텍스트로 변환
        table_text = '\n'.join(lines)
        
        # 특정 패턴 인식 (예: 매출, 영업이익 등)
        if any(keyword in table_text for keyword in ['매출', '영업이익', '자산', '부채']):
            return {
                'type': 'financial',
                'content': table_text,
                'parsed': self._parse_financial_table(table_text)
            }
        
        return {
            'type': 'general',
            'content': table_text
        }
    
    def _parse_financial_table(self, table_text: str) -> Dict:
        """재무 표 파싱"""
        parsed = {}
        
        # 패턴 매칭으로 주요 수치 추출
        patterns = [
            (r'DX.*?(\d+[\d,]*)\s*(조|억)', 'DX_매출'),
            (r'DS.*?(\d+[\d,]*)\s*(조|억)', 'DS_매출'),
            (r'매출.*?(\d+[\d,]*)\s*(조|억)', '총매출'),
            (r'영업이익.*?(\d+[\d,]*)\s*(조|억)', '영업이익'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, table_text)
            if match:
                value = match.group(1).replace(',', '')
                unit = match.group(2)
                parsed[key] = f"{value}{unit}"
        
        return parsed
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        # 중복 문자 제거
        text = re.sub(r'([A-Z])\1+', r'\1', text)  # AA -> A
        text = re.sub(r'([a-z])\1{2,}', r'\1', text)  # aaa -> a
        
        # 특정 패턴 수정
        replacements = [
            (r'AA JJoouurrnneeyy TT oowwaarrddss', 'A Journey Towards'),
            (r'aa SSuussttaa?ii?nnaabbllee FFuuttuurree', 'a Sustainable Future'),
            (r'([가-힣])\1+', r'\1'),  # 한글 중복 제거
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        
        # 불필요한 공백 정리
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _create_structured_content(self, text: str, tables: List[Dict], page_num: int) -> str:
        """구조화된 콘텐츠 생성"""
        content = [f"## 페이지 {page_num}\n"]
        
        # 주요 제목 추출
        lines = text.split('\n')
        for line in lines[:5]:  # 처음 5줄에서 제목 찾기
            if len(line) > 10 and len(line) < 100:
                if any(keyword in line for keyword in ['CEO', '메시지', '개요', '성과', '목표']):
                    content.append(f"### {line.strip()}\n")
                    break
        
        # 표 데이터를 구조화된 텍스트로 변환
        if tables:
            content.append("\n### 📊 주요 데이터\n")
            for table in tables:
                if table['type'] == 'financial' and table.get('parsed'):
                    content.append("\n**재무 성과:**\n")
                    for key, value in table['parsed'].items():
                        clean_key = key.replace('_', ' ')
                        content.append(f"- {clean_key}: {value}\n")
                else:
                    content.append(f"\n```\n{table['content']}\n```\n")
        
        # 본문 텍스트 추가
        content.append("\n### 본문\n")
        
        # 긴 텍스트를 문단으로 분리
        paragraphs = self._split_into_paragraphs(text)
        for para in paragraphs:
            if len(para) > 50:  # 의미 있는 길이의 문단만
                content.append(f"\n{para}\n")
        
        return ''.join(content)
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """텍스트를 문단으로 분리"""
        # 문장 단위로 분리
        sentences = re.split(r'[.!?]\s+', text)
        
        paragraphs = []
        current_para = []
        
        for sentence in sentences:
            current_para.append(sentence)
            
            # 3-5 문장마다 문단 구분
            if len(current_para) >= 3:
                para_text = '. '.join(current_para) + '.'
                if len(para_text) > 100:
                    paragraphs.append(para_text)
                    current_para = []
        
        # 남은 문장 처리
        if current_para:
            paragraphs.append('. '.join(current_para) + '.')
        
        return paragraphs
    
    def refine_with_llm(self, content: str) -> str:
        """Gemini를 사용해 텍스트 정제"""
        prompt = f"""
        다음 텍스트는 PDF에서 추출된 것입니다. 다음 작업을 수행해주세요:
        
        1. 중복된 문자 수정 (예: AA JJoouurrnneeyy → A Journey)
        2. 분리된 숫자와 단위 결합 (예: 174 조 8,877 억 원 → 174조 8,877억원)
        3. 표 데이터를 구조화된 텍스트로 변환
        4. 문맥상 의미가 통하도록 문장 정리
        
        원본 텍스트:
        {content[:2000]}  # API 한계로 일부만 전송
        
        정제된 텍스트만 출력하세요:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"LLM 정제 오류: {e}")
            return content
    
    def save_as_markdown(self, output_path: Path):
        """마크다운 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 삼성전자 지속가능경영 보고서 2025\n")
            f.write("*PyMuPDF와 Gemini로 추출 및 정제*\n\n")
            f.write("---\n\n")
            
            for page_data in self.extracted_content:
                f.write(page_data['structured_content'])
                f.write("\n\n---\n\n")
        
        print(f"✅ 저장 완료: {output_path}")


def main():
    pdf_path = Path("/Users/donghyunkim/Desktop/joo_project/Samsung_Electronics_Sustainability_Report_2025_KOR.pdf")
    output_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_advanced.md")
    
    # 추출기 생성
    extractor = AdvancedPDFExtractor(pdf_path)
    
    # PDF 추출
    content = extractor.extract()
    
    # 마크다운 저장
    extractor.save_as_markdown(output_path)
    
    # 샘플 LLM 정제 (처음 3페이지만)
    print("\n🤖 Gemini로 텍스트 정제 중...")
    for i in range(min(3, len(content))):
        refined = extractor.refine_with_llm(content[i]['text'])
        print(f"\n페이지 {i+1} 정제 결과 (일부):")
        print(refined[:300] + "...")
    
    return output_path


if __name__ == "__main__":
    output = main()
    print(f"\n✅ 완료! 다음 파일을 확인하세요: {output}")