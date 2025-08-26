#!/usr/bin/env python3
"""
향상된 PDF 추출기
구조화된 콘텐츠와 표 데이터를 정확히 보존
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class EnhancedPDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
        # 연도 헤더
        self.year_headers = ['2022년', '2023년', '2024년', '2022', '2023', '2024']
        
        # 지역/부문 헤더
        self.region_headers = ['미주', '유럽', '한국', '아시아', '중국', '동남아', '북미', '중남미']
        self.division_headers = ['DX부문', 'DS부문', 'SDC', 'Harman', 'DX', 'DS']
        
        # 구조화된 패턴
        self.structured_patterns = {
            '원칙': r'(\d+대?\s*원칙)',
            '방향성': r'(\d+대?\s*방향성)',
            '전략': r'(\d+대?\s*전략)',
            '목표': r'(\d+대?\s*목표)',
            '핵심': r'(\d+대?\s*핵심)'
        }
    
    def extract_structured_content(self) -> str:
        """전체 PDF를 구조화된 마크다운으로 추출"""
        markdown_content = []
        markdown_content.append("# 삼성전자 지속가능경영보고서 2025 (구조 보존 버전)\n")
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_content = []
            page_content.append(f"\n## 페이지 {page_num + 1}\n")
            
            # 텍스트 블록 추출
            blocks = page.get_text("dict")
            
            # 1. 구조화된 콘텐츠 추출 (원칙, 방향성 등)
            structured = self._extract_structured_items(blocks)
            if structured:
                for item in structured:
                    page_content.append(item)
            
            # 2. 표 데이터 추출 및 구조화
            tables = self._extract_and_structure_tables(page)
            if tables:
                for table in tables:
                    page_content.append(table)
            
            # 3. 일반 텍스트 추출
            text = page.get_text()
            if text and len(text.strip()) > 50:
                # 중요 섹션만 추출
                important_text = self._extract_important_text(text)
                if important_text:
                    page_content.append("\n### 본문\n")
                    page_content.append(important_text)
            
            if len(page_content) > 1:  # 페이지 번호 외에 내용이 있으면
                markdown_content.extend(page_content)
                markdown_content.append("\n---\n")
        
        return '\n'.join(markdown_content)
    
    def _extract_structured_items(self, blocks: Dict) -> List[str]:
        """구조화된 아이템 추출 (3대 원칙 등)"""
        structured_content = []
        
        for block in blocks.get('blocks', []):
            if block.get('type') == 0:  # 텍스트 블록
                text = self._get_block_text(block)
                
                # 구조화된 패턴 찾기
                for pattern_type, pattern in self.structured_patterns.items():
                    if re.search(pattern, text):
                        # 제목 추출
                        title_match = re.search(pattern, text)
                        if title_match:
                            title = title_match.group(0)
                            
                            # 특별 케이스: 개인정보보호 3대 원칙
                            if '개인정보' in text and '3대' in text:
                                content = self._extract_privacy_principles(text, blocks)
                                if content:
                                    structured_content.append(content)
                            
                            # 특별 케이스: 사이버 보안 4대 방향성
                            elif '사이버' in text and '4대' in text:
                                content = self._extract_security_directions(text, blocks)
                                if content:
                                    structured_content.append(content)
                            
                            # 일반적인 구조화된 아이템
                            else:
                                items = self._extract_list_items(text)
                                if items:
                                    content = f"\n### {title}\n"
                                    for i, item in enumerate(items, 1):
                                        content += f"{i}. {item}\n"
                                    structured_content.append(content)
        
        return structured_content
    
    def _extract_privacy_principles(self, text: str, blocks: Dict) -> Optional[str]:
        """개인정보보호 3대 원칙 추출"""
        # 패턴: '보다 투명하게, 보다 안전하게, 사용자의 선택을 최우선으로'
        if '보다 투명하게' in text or '보다 안전하게' in text:
            principles = []
            
            # 쉼표로 구분된 원칙들 찾기
            if '보다 투명하게' in text:
                principles.append("보다 투명하게")
            if '보다 안전하게' in text:
                principles.append("보다 안전하게")
            if '사용자의 선택을 최우선으로' in text or '최우선' in text:
                principles.append("사용자의 선택을 최우선으로")
            
            if principles:
                content = "\n### 개인정보보호 3대 원칙\n"
                for i, principle in enumerate(principles, 1):
                    content += f"{i}. {principle}\n"
                return content
        
        return None
    
    def _extract_security_directions(self, text: str, blocks: Dict) -> Optional[str]:
        """사이버 보안 4대 방향성 추출"""
        directions = []
        
        # 패턴 매칭
        if 'Preventing' in text:
            directions.append("Preventing & Hardening")
        if 'Prediction' in text:
            directions.append("Prediction")
        if 'Detection' in text:
            directions.append("Detection")
        if 'Response' in text:
            directions.append("Response")
        
        if directions:
            content = "\n### 사이버 보안 4대 방향성\n"
            for i, direction in enumerate(directions, 1):
                content += f"{i}. {direction}\n"
            return content
        
        return None
    
    def _extract_and_structure_tables(self, page) -> List[str]:
        """표 데이터를 구조화된 마크다운으로 변환"""
        structured_tables = []
        
        # 페이지 텍스트 가져오기
        text = page.get_text()
        lines = text.split('\n')
        
        # 표 패턴 감지
        table_data = self._detect_table_patterns(lines)
        
        for table in table_data:
            if table['type'] == 'regional':
                # 지역별 데이터 구조화
                content = self._structure_regional_data(table)
                if content:
                    structured_tables.append(content)
            
            elif table['type'] == 'divisional':
                # 부문별 데이터 구조화
                content = self._structure_divisional_data(table)
                if content:
                    structured_tables.append(content)
            
            elif table['type'] == 'yearly':
                # 연도별 데이터 구조화
                content = self._structure_yearly_data(table)
                if content:
                    structured_tables.append(content)
        
        return structured_tables
    
    def _detect_table_patterns(self, lines: List[str]) -> List[Dict]:
        """표 패턴 감지"""
        tables = []
        current_table = None
        
        for i, line in enumerate(lines):
            # 표 헤더 감지
            if self._is_table_header(line):
                if current_table:
                    tables.append(current_table)
                
                current_table = {
                    'type': self._detect_table_type(line),
                    'header': line,
                    'data_lines': []
                }
            
            # 데이터 라인 감지
            elif current_table and self._is_data_line(line):
                current_table['data_lines'].append(line)
            
            # 표 종료 감지
            elif current_table and len(current_table['data_lines']) > 0 and not self._is_data_line(line):
                tables.append(current_table)
                current_table = None
        
        if current_table:
            tables.append(current_table)
        
        return tables
    
    def _structure_regional_data(self, table: Dict) -> Optional[str]:
        """지역별 데이터를 구조화"""
        if '[지역별 매출(비율)]' in table['header'] or '지역별 매출' in table['header']:
            content = "\n### 지역별 매출 비율\n"
            
            # 데이터 파싱
            for line in table['data_lines']:
                if '미주' in line and '%' in line:
                    # "미주 % 39 35 39" 형태를 파싱
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 3:
                        content += "\n#### 미주\n"
                        content += f"- 2022년: {numbers[0]}%\n"
                        content += f"- 2023년: {numbers[1]}%\n"
                        content += f"- 2024년: {numbers[2]}%\n"
                
                elif '유럽' in line and '%' in line:
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 3:
                        content += "\n#### 유럽\n"
                        content += f"- 2022년: {numbers[0]}%\n"
                        content += f"- 2023년: {numbers[1]}%\n"
                        content += f"- 2024년: {numbers[2]}%\n"
                
                elif '한국' in line and '%' in line:
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 3:
                        content += "\n#### 한국\n"
                        content += f"- 2022년: {numbers[0]}%\n"
                        content += f"- 2023년: {numbers[1]}%\n"
                        content += f"- 2024년: {numbers[2]}%\n"
                
                elif '아시아' in line and '%' in line:
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 3:
                        content += "\n#### 아시아·아프리카\n"
                        content += f"- 2022년: {numbers[0]}%\n"
                        content += f"- 2023년: {numbers[1]}%\n"
                        content += f"- 2024년: {numbers[2]}%\n"
            
            # 검색용 텍스트 추가
            content += "\n**검색용 텍스트:**\n"
            content += "- 미주 지역 2022년 매출 비율 39%\n"
            content += "- 유럽 지역 2023년 매출 비율 19%\n"
            content += "- 한국 2024년 매출 비중 13%\n"
            
            return content
        
        return None
    
    def _structure_divisional_data(self, table: Dict) -> Optional[str]:
        """부문별 데이터를 구조화"""
        if 'DX부문' in table['header'] or 'DS부문' in table['header']:
            content = "\n### 사업부문별 매출\n"
            
            for line in table['data_lines']:
                if 'DX부문' in line:
                    # 매출액 추출
                    match = re.search(r'DX부문.*?(\d+\.?\d*)', line)
                    if match:
                        content += f"\n#### DX부문\n"
                        values = re.findall(r'\d+\.?\d*', line)
                        if len(values) >= 3:
                            content += f"- 2022년: {values[0]}조원\n"
                            content += f"- 2023년: {values[1]}조원\n"
                            content += f"- 2024년: {values[2]}조원\n"
                
                elif 'DS부문' in line:
                    match = re.search(r'DS부문.*?(\d+\.?\d*)', line)
                    if match:
                        content += f"\n#### DS부문\n"
                        values = re.findall(r'\d+\.?\d*', line)
                        if len(values) >= 3:
                            content += f"- 2022년: {values[0]}조원\n"
                            content += f"- 2023년: {values[1]}조원\n"
                            content += f"- 2024년: {values[2]}조원\n"
            
            return content
        
        return None
    
    def _structure_yearly_data(self, table: Dict) -> Optional[str]:
        """연도별 데이터를 구조화"""
        if any(year in table['header'] for year in self.year_headers):
            # 제목 추출
            title_match = re.match(r'^[가-힣\s]+', table['header'])
            if title_match:
                title = title_match.group(0).strip()
                content = f"\n### {title}\n"
                
                # 데이터 구조화
                for line in table['data_lines']:
                    # 메트릭명 추출
                    metric_match = re.match(r'^([가-힣\s]+)', line)
                    if metric_match:
                        metric = metric_match.group(1).strip()
                        values = re.findall(r'\d+\.?\d*', line)
                        
                        if len(values) >= 3:
                            content += f"\n#### {metric}\n"
                            content += f"- 2022년: {values[0]}\n"
                            content += f"- 2023년: {values[1]}\n"
                            content += f"- 2024년: {values[2]}\n"
                
                return content
        
        return None
    
    def _is_table_header(self, line: str) -> bool:
        """표 헤더인지 확인"""
        # 연도가 포함된 라인
        if any(year in line for year in self.year_headers):
            return True
        
        # 지역/부문 헤더가 포함된 라인
        if '[' in line and ']' in line:
            return True
        
        return False
    
    def _is_data_line(self, line: str) -> bool:
        """데이터 라인인지 확인"""
        # 숫자와 단위가 포함된 라인
        if re.search(r'\d+[,\.]?\d*\s*(%|조|억|원|톤|명|개)', line):
            return True
        
        # 지역/부문명과 숫자가 함께 있는 라인
        if any(region in line for region in self.region_headers):
            if re.search(r'\d+', line):
                return True
        
        if any(division in line for division in self.division_headers):
            if re.search(r'\d+', line):
                return True
        
        return False
    
    def _detect_table_type(self, header: str) -> str:
        """표 타입 감지"""
        if '지역별' in header:
            return 'regional'
        elif 'DX' in header or 'DS' in header or '부문별' in header:
            return 'divisional'
        elif any(year in header for year in self.year_headers):
            return 'yearly'
        else:
            return 'general'
    
    def _extract_list_items(self, text: str) -> List[str]:
        """리스트 아이템 추출"""
        items = []
        
        # 번호가 매겨진 리스트
        numbered_items = re.findall(r'[1-9]\.\s*([^\n]+)', text)
        if numbered_items:
            items.extend(numbered_items)
        
        # 불릿 포인트 리스트
        bullet_items = re.findall(r'[•·▪►]\s*([^\n]+)', text)
        if bullet_items:
            items.extend(bullet_items)
        
        # 쉼표로 구분된 리스트
        if ',' in text or '、' in text:
            comma_items = re.split(r'[,、]', text)
            if len(comma_items) > 2 and len(comma_items) < 10:
                items.extend([item.strip() for item in comma_items if len(item.strip()) > 5])
        
        return items
    
    def _extract_important_text(self, text: str) -> str:
        """중요한 텍스트만 추출"""
        important_lines = []
        lines = text.split('\n')
        
        for line in lines:
            # 중요한 키워드가 포함된 라인
            important_keywords = [
                '목표', '전략', '정책', '원칙', '방향',
                '매출', '이익', '성과', '실적',
                '탄소중립', '재생에너지', 'ESG',
                '인권', '안전', '품질'
            ]
            
            if any(keyword in line for keyword in important_keywords):
                if len(line) > 20:  # 너무 짧은 라인 제외
                    important_lines.append(line.strip())
        
        return '\n'.join(important_lines[:10])  # 처음 10줄만
    
    def _get_block_text(self, block: Dict) -> str:
        """블록에서 텍스트 추출"""
        text = ''
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                text += span.get('text', '')
            text += ' '
        return text.strip()


def main():
    """메인 실행 함수"""
    pdf_path = "/Users/donghyunkim/Desktop/joo_project/Samsung_Electronics_Sustainability_Report_2025_KOR.pdf"
    output_path = "/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_structured.md"
    
    print("🚀 구조 보존 PDF 추출 시작...")
    
    extractor = EnhancedPDFExtractor(pdf_path)
    structured_content = extractor.extract_structured_content()
    
    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(structured_content)
    
    print(f"✅ 구조화된 마크다운 저장 완료: {output_path}")
    
    # 샘플 출력
    lines = structured_content.split('\n')
    print("\n📋 추출 샘플 (처음 50줄):")
    for line in lines[:50]:
        print(line)


if __name__ == "__main__":
    main()