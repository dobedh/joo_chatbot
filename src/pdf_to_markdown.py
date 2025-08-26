#!/usr/bin/env python3
"""
PDF를 구조화된 마크다운으로 변환
표, 리스트, 섹션을 적절히 처리하여 벡터 DB에 최적화된 형태로 변환
"""

import pdfplumber
from pathlib import Path
import re
from typing import List, Dict, Optional
import json

class PDFToMarkdownConverter:
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.markdown_content = []
        self.current_section = None
        self.section_hierarchy = []
        
    def convert(self) -> str:
        """PDF를 마크다운으로 변환"""
        print(f"📚 PDF 파일 처리 시작: {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"총 페이지 수: {total_pages}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"처리 중: 페이지 {page_num}/{total_pages}")
                self._process_page(page, page_num)
        
        return "\n\n".join(self.markdown_content)
    
    def _process_page(self, page, page_num: int):
        """각 페이지 처리"""
        # 페이지 구분자 추가
        self.markdown_content.append(f"\n---\n## 📄 페이지 {page_num}\n")
        
        # 텍스트 추출
        text = page.extract_text()
        
        # 표 추출
        tables = page.extract_tables()
        
        if tables:
            # 표가 있는 경우 처리
            self._process_tables(tables, page_num)
            
        if text:
            # 텍스트 구조화
            structured_text = self._structure_text(text, page_num)
            self.markdown_content.append(structured_text)
    
    def _process_tables(self, tables: List, page_num: int):
        """표를 마크다운 형식으로 변환"""
        for i, table in enumerate(tables, 1):
            self.markdown_content.append(f"\n### 📊 표 {page_num}-{i}\n")
            
            # 표를 설명적 텍스트로 변환
            table_text = self._table_to_descriptive_text(table)
            self.markdown_content.append(table_text)
            
            # 원본 표도 마크다운 테이블로 보존
            markdown_table = self._table_to_markdown(table)
            if markdown_table:
                self.markdown_content.append("\n**원본 데이터:**")
                self.markdown_content.append(markdown_table)
    
    def _table_to_descriptive_text(self, table: List[List]) -> str:
        """표를 설명적 텍스트로 변환"""
        if not table or not table[0]:
            return ""
        
        descriptions = []
        
        # 헤더가 있다고 가정
        headers = [str(cell).strip() if cell else "" for cell in table[0]]
        
        for row_idx, row in enumerate(table[1:], 1):
            if not row or all(not cell for cell in row):
                continue
                
            row_description = []
            for col_idx, cell in enumerate(row):
                if cell and col_idx < len(headers) and headers[col_idx]:
                    # "항목: 값" 형태로 변환
                    clean_value = str(cell).strip().replace('\n', ' ')
                    if clean_value and clean_value != '-':
                        row_description.append(f"{headers[col_idx]}: {clean_value}")
            
            if row_description:
                descriptions.append("• " + ", ".join(row_description))
        
        return "\n".join(descriptions)
    
    def _table_to_markdown(self, table: List[List]) -> str:
        """표를 마크다운 테이블로 변환"""
        if not table or len(table) < 2:
            return ""
        
        # 빈 셀 처리
        cleaned_table = []
        for row in table:
            cleaned_row = [str(cell).strip() if cell else "-" for cell in row]
            cleaned_table.append(cleaned_row)
        
        # 마크다운 테이블 생성
        markdown_lines = []
        
        # 헤더
        markdown_lines.append("| " + " | ".join(cleaned_table[0]) + " |")
        markdown_lines.append("|" + "---|" * len(cleaned_table[0]))
        
        # 데이터 행
        for row in cleaned_table[1:]:
            markdown_lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(markdown_lines)
    
    def _structure_text(self, text: str, page_num: int) -> str:
        """텍스트를 구조화"""
        lines = text.split('\n')
        structured_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 제목/섹션 감지
            if self._is_header(line):
                structured_lines.append(f"\n### {line}\n")
                self.current_section = line
            # 불릿 포인트 감지
            elif self._is_bullet_point(line):
                structured_lines.append(f"- {self._clean_bullet(line)}")
            # 숫자 리스트 감지
            elif self._is_numbered_list(line):
                structured_lines.append(f"{line}")
            # 일반 텍스트
            else:
                structured_lines.append(line)
        
        # 메타데이터 추가
        if self.current_section:
            structured_lines.insert(0, f"**[섹션: {self.current_section}]**")
        
        return "\n".join(structured_lines)
    
    def _is_header(self, text: str) -> bool:
        """제목인지 판단"""
        # 짧고 대문자가 많거나 특정 키워드로 시작
        header_keywords = ['개요', '목표', '전략', '성과', '계획', '정책', '원칙']
        
        if len(text) < 50:  # 짧은 텍스트
            if any(keyword in text for keyword in header_keywords):
                return True
            # 숫자로 시작하는 섹션
            if re.match(r'^\d+\.?\s+\w+', text):
                return True
        return False
    
    def _is_bullet_point(self, text: str) -> bool:
        """불릿 포인트인지 판단"""
        bullet_patterns = [r'^[•·▪▸◦]', r'^[-*]', r'^[①②③④⑤⑥⑦⑧⑨⑩]']
        return any(re.match(pattern, text) for pattern in bullet_patterns)
    
    def _is_numbered_list(self, text: str) -> bool:
        """숫자 리스트인지 판단"""
        return re.match(r'^\d+[\.\)]\s+', text) is not None
    
    def _clean_bullet(self, text: str) -> str:
        """불릿 포인트 정리"""
        # 불릿 문자 제거
        text = re.sub(r'^[•·▪▸◦\-*①②③④⑤⑥⑦⑧⑨⑩]\s*', '', text)
        return text.strip()
    
    def save_to_file(self, content: str, output_path: Path):
        """마크다운 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            # 메타데이터 헤더 추가
            f.write("# 삼성전자 지속가능경영 보고서 2025\n")
            f.write("*PDF에서 추출 및 구조화된 텍스트*\n\n")
            f.write("---\n\n")
            f.write(content)
        
        print(f"✅ 마크다운 파일 저장 완료: {output_path}")


def main():
    # 경로 설정
    pdf_path = Path("/Users/donghyunkim/Desktop/joo_project/Samsung_Electronics_Sustainability_Report_2025_KOR.pdf")
    output_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_processed.md")
    
    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 변환 실행
    converter = PDFToMarkdownConverter(pdf_path)
    markdown_content = converter.convert()
    
    # 파일 저장
    converter.save_to_file(markdown_content, output_path)
    
    # 통계 출력
    print("\n📊 변환 통계:")
    print(f"- 총 문자 수: {len(markdown_content):,}")
    print(f"- 총 줄 수: {markdown_content.count(chr(10)):,}")
    print(f"- 섹션 수: {markdown_content.count('###')}")
    print(f"- 표 수: {markdown_content.count('📊 표')}")
    
    return output_path


if __name__ == "__main__":
    output_file = main()
    print(f"\n🎯 다음 단계: {output_file} 파일을 벡터 DB로 변환하세요.")