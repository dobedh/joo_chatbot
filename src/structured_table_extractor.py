#!/usr/bin/env python3
"""
구조화된 표 데이터 추출기
PDF에서 표 데이터를 정확히 추출하고 구조화
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class StructuredTableExtractor:
    def __init__(self):
        # 연도 패턴
        self.year_pattern = r'(2022|2023|2024)년?'
        
        # 단위 패턴
        self.unit_patterns = {
            'percent': r'%',
            'trillion': r'조\s*원?',
            'billion': r'억\s*원?',
            'million': r'만\s*원?',
            'ton': r'톤',
            'person': r'명',
            'count': r'개'
        }
    
    def extract_tables_from_text(self, text: str) -> List[Dict]:
        """텍스트에서 표 데이터 추출 및 구조화"""
        tables = []
        lines = text.split('\n')
        
        # 페이지별로 처리
        current_page = None
        page_lines = []
        
        for line in lines:
            # 페이지 구분
            if '## 페이지' in line:
                if current_page and page_lines:
                    # 이전 페이지 처리
                    page_tables = self._process_page_lines(page_lines, current_page)
                    tables.extend(page_tables)
                
                # 새 페이지 시작
                current_page = line
                page_lines = []
            else:
                page_lines.append(line)
        
        # 마지막 페이지 처리
        if current_page and page_lines:
            page_tables = self._process_page_lines(page_lines, current_page)
            tables.extend(page_tables)
        
        return tables
    
    def _process_page_lines(self, lines: List[str], page_info: str) -> List[Dict]:
        """페이지 라인들을 처리하여 표 추출"""
        tables = []
        
        # 지역별 매출 표 찾기
        regional_table = self._extract_regional_sales_table(lines)
        if regional_table:
            regional_table['page'] = page_info
            tables.append(regional_table)
        
        # 사업부문별 매출 표 찾기
        divisional_table = self._extract_divisional_sales_table(lines)
        if divisional_table:
            divisional_table['page'] = page_info
            tables.append(divisional_table)
        
        # 재무 성과 표 찾기
        financial_table = self._extract_financial_table(lines)
        if financial_table:
            financial_table['page'] = page_info
            tables.append(financial_table)
        
        # 환경 데이터 표 찾기
        environmental_table = self._extract_environmental_table(lines)
        if environmental_table:
            environmental_table['page'] = page_info
            tables.append(environmental_table)
        
        return tables
    
    def _extract_regional_sales_table(self, lines: List[str]) -> Optional[Dict]:
        """지역별 매출 표 추출"""
        # 패턴: [지역별 매출(비율)] 또는 지역별 매출
        header_found = False
        data_lines = []
        
        for i, line in enumerate(lines):
            if '지역별 매출' in line and ('비율' in line or '%' in line):
                header_found = True
                continue
            
            if header_found:
                # 데이터 라인 수집
                if any(region in line for region in ['미주', '유럽', '한국', '아시아']):
                    data_lines.append(line)
                elif len(data_lines) > 0 and '---' in line:
                    break  # 표 끝
        
        if not data_lines:
            return None
        
        # 구조화된 데이터 생성
        table = {
            'type': 'regional_sales',
            'title': '지역별 매출 비율',
            'data': {},
            'markdown': ''
        }
        
        # 데이터 파싱
        for line in data_lines:
            if '미주' in line:
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    table['data']['미주'] = {
                        '2022년': f"{numbers[0]}%",
                        '2023년': f"{numbers[1]}%",
                        '2024년': f"{numbers[2]}%"
                    }
            elif '유럽' in line:
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    table['data']['유럽'] = {
                        '2022년': f"{numbers[0]}%",
                        '2023년': f"{numbers[1]}%",
                        '2024년': f"{numbers[2]}%"
                    }
            elif '한국' in line:
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    table['data']['한국'] = {
                        '2022년': f"{numbers[0]}%",
                        '2023년': f"{numbers[1]}%",
                        '2024년': f"{numbers[2]}%"
                    }
            elif '아시아' in line:
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 3:
                    table['data']['아시아·아프리카'] = {
                        '2022년': f"{numbers[0]}%",
                        '2023년': f"{numbers[1]}%",
                        '2024년': f"{numbers[2]}%"
                    }
        
        # 마크다운 생성
        if table['data']:
            table['markdown'] = self._generate_regional_markdown(table['data'])
        
        return table if table['data'] else None
    
    def _extract_divisional_sales_table(self, lines: List[str]) -> Optional[Dict]:
        """사업부문별 매출 표 추출"""
        header_found = False
        data_lines = []
        
        for i, line in enumerate(lines):
            if '사업부문별 매출' in line or ('DX부문' in line and 'DS부문' in line):
                header_found = True
                continue
            
            if header_found:
                if 'DX부문' in line or 'DS부문' in line or 'SDC' in line or 'Harman' in line:
                    data_lines.append(line)
                elif len(data_lines) > 0 and ('---' in line or '[' in line):
                    break
        
        if not data_lines:
            return None
        
        table = {
            'type': 'divisional_sales',
            'title': '사업부문별 매출',
            'data': {},
            'markdown': ''
        }
        
        # 데이터 파싱
        for line in data_lines:
            if 'DX부문' in line:
                # 조 원 단위 찾기
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 3:
                    table['data']['DX부문'] = {
                        '2022년': f"{numbers[0]}조원",
                        '2023년': f"{numbers[1]}조원",
                        '2024년': f"{numbers[2]}조원"
                    }
            elif 'DS부문' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 3:
                    table['data']['DS부문'] = {
                        '2022년': f"{numbers[0]}조원",
                        '2023년': f"{numbers[1]}조원",
                        '2024년': f"{numbers[2]}조원"
                    }
        
        # 마크다운 생성
        if table['data']:
            table['markdown'] = self._generate_divisional_markdown(table['data'])
        
        return table if table['data'] else None
    
    def _extract_financial_table(self, lines: List[str]) -> Optional[Dict]:
        """재무 성과 표 추출"""
        header_found = False
        data_lines = []
        
        for i, line in enumerate(lines):
            if '핵심 재무 성과' in line or ('매출액' in line and '영업이익' in line):
                header_found = True
                continue
            
            if header_found:
                if any(metric in line for metric in ['매출액', '영업이익', '당기순이익']):
                    data_lines.append(line)
                elif len(data_lines) > 0 and '---' in line:
                    break
        
        if not data_lines:
            return None
        
        table = {
            'type': 'financial_performance',
            'title': '핵심 재무 성과',
            'data': {},
            'markdown': ''
        }
        
        # 데이터 파싱
        for line in data_lines:
            if '매출액' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 3:
                    table['data']['매출액'] = {
                        '2022년': f"{numbers[0]}조원",
                        '2023년': f"{numbers[1]}조원",
                        '2024년': f"{numbers[2]}조원"
                    }
            elif '영업이익' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 3:
                    table['data']['영업이익'] = {
                        '2022년': f"{numbers[0]}조원",
                        '2023년': f"{numbers[1]}조원",
                        '2024년': f"{numbers[2]}조원"
                    }
            elif '당기순이익' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if len(numbers) >= 3:
                    table['data']['당기순이익'] = {
                        '2022년': f"{numbers[0]}조원",
                        '2023년': f"{numbers[1]}조원",
                        '2024년': f"{numbers[2]}조원"
                    }
        
        # 마크다운 생성
        if table['data']:
            table['markdown'] = self._generate_financial_markdown(table['data'])
        
        return table if table['data'] else None
    
    def _extract_environmental_table(self, lines: List[str]) -> Optional[Dict]:
        """환경 데이터 표 추출"""
        # 재생에너지, 탄소배출, 폐기물 등
        table = {
            'type': 'environmental',
            'title': '환경 성과',
            'data': {},
            'markdown': ''
        }
        
        for i, line in enumerate(lines):
            if '재생에너지 전환율' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if numbers:
                    table['data']['재생에너지 전환율'] = {
                        '값': f"{numbers[0]}%"
                    }
            elif '탄소배출' in line:
                numbers = re.findall(r'(\d+\.?\d*)', line)
                if numbers:
                    table['data']['탄소배출량'] = {
                        '값': f"{numbers[0]}톤"
                    }
        
        return table if table['data'] else None
    
    def _generate_regional_markdown(self, data: Dict) -> str:
        """지역별 매출 마크다운 생성"""
        md = "### 지역별 매출 비율\n\n"
        
        for region, years in data.items():
            md += f"#### {region}\n"
            for year, value in years.items():
                md += f"- {year}: {value}\n"
            md += "\n"
        
        # 검색용 텍스트 추가
        md += "**검색용 텍스트:**\n"
        for region, years in data.items():
            for year, value in years.items():
                md += f"- {region} {year} 매출 비율 {value}\n"
                md += f"- {year} {region} 지역 매출은 전체의 {value}\n"
        
        return md
    
    def _generate_divisional_markdown(self, data: Dict) -> str:
        """사업부문별 매출 마크다운 생성"""
        md = "### 사업부문별 매출\n\n"
        
        for division, years in data.items():
            md += f"#### {division}\n"
            for year, value in years.items():
                md += f"- {year}: {value}\n"
            md += "\n"
        
        # 검색용 텍스트 추가
        md += "**검색용 텍스트:**\n"
        for division, years in data.items():
            for year, value in years.items():
                md += f"- {division} {year} 매출 {value}\n"
                md += f"- {year} {division} 매출액은 {value}\n"
        
        return md
    
    def _generate_financial_markdown(self, data: Dict) -> str:
        """재무 성과 마크다운 생성"""
        md = "### 핵심 재무 성과\n\n"
        
        for metric, years in data.items():
            md += f"#### {metric}\n"
            for year, value in years.items():
                md += f"- {year}: {value}\n"
            md += "\n"
        
        # 검색용 텍스트 추가
        md += "**검색용 텍스트:**\n"
        for metric, years in data.items():
            for year, value in years.items():
                md += f"- {year} {metric} {value}\n"
                md += f"- 삼성전자 {year} {metric}은 {value}\n"
        
        return md


def process_existing_markdown(input_path: str, output_path: str):
    """기존 마크다운 파일을 처리하여 표 구조화"""
    
    print("📊 표 데이터 구조화 시작...")
    
    # 파일 읽기
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 표 추출기 초기화
    extractor = StructuredTableExtractor()
    
    # 표 추출
    tables = extractor.extract_tables_from_text(content)
    
    print(f"✅ {len(tables)}개 표 발견")
    
    # 구조화된 콘텐츠 생성
    structured_content = []
    structured_content.append("# 삼성전자 지속가능경영보고서 2025 (완전 구조화 버전)\n")
    
    # 원본 내용 처리
    lines = content.split('\n')
    skip_lines = 0
    
    for i, line in enumerate(lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue
        
        # 표 영역 감지 및 대체
        table_replaced = False
        for table in tables:
            if table['type'] == 'regional_sales' and '지역별 매출' in line:
                structured_content.append(table['markdown'])
                skip_lines = 10  # 원본 표 영역 스킵
                table_replaced = True
                break
            elif table['type'] == 'divisional_sales' and '사업부문별 매출' in line:
                structured_content.append(table['markdown'])
                skip_lines = 10
                table_replaced = True
                break
            elif table['type'] == 'financial_performance' and '핵심 재무 성과' in line:
                structured_content.append(table['markdown'])
                skip_lines = 10
                table_replaced = True
                break
        
        if not table_replaced:
            structured_content.append(line)
    
    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(structured_content))
    
    print(f"✅ 구조화된 파일 저장: {output_path}")
    
    # 샘플 출력
    for table in tables[:3]:
        print(f"\n📋 {table['title']}:")
        print(table['markdown'][:500])


def main():
    """메인 실행 함수"""
    input_path = "/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_advanced.md"
    output_path = "/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_fully_structured.md"
    
    process_existing_markdown(input_path, output_path)


if __name__ == "__main__":
    main()