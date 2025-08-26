#!/usr/bin/env python3
"""
마크다운 파일을 정제하고 벡터 DB에 최적화
"""

import re
from pathlib import Path
from typing import List, Dict

class MarkdownCleaner:
    def __init__(self, input_path: Path):
        self.input_path = input_path
        self.sections = []
        
    def clean(self) -> str:
        """마크다운 파일 정제"""
        print("🧹 마크다운 정제 시작...")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 중복 문자 제거
        content = self._fix_duplicated_chars(content)
        
        # 2. 빈 줄 정리
        content = self._clean_empty_lines(content)
        
        # 3. 섹션별로 분할
        sections = self._split_into_sections(content)
        
        # 4. 각 섹션 정제
        cleaned_sections = []
        for section in sections:
            cleaned = self._clean_section(section)
            if cleaned:
                cleaned_sections.append(cleaned)
        
        return "\n\n".join(cleaned_sections)
    
    def _fix_duplicated_chars(self, text: str) -> str:
        """중복된 문자 수정"""
        # AA JJoouurrnneeyy -> A Journey
        patterns = [
            (r'AA JJoouurrnneeyy TT oowwaarrddss', 'A Journey Towards'),
            (r'aa SSuussttaa?ii?nnaabbllee FFuuttuurree', 'a Sustainable Future'),
            (r'삼삼성성전전자자', '삼성전자'),
            (r'지지속속가가능능경경영영', '지속가능경영'),
            (r'보보고고서서', '보고서'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        # 일반적인 중복 문자 패턴 제거 (같은 문자가 2번 이상 반복)
        text = re.sub(r'([가-힣])\1{2,}', r'\1', text)
        
        return text
    
    def _clean_empty_lines(self, text: str) -> str:
        """빈 줄 정리"""
        # 3줄 이상의 빈 줄을 2줄로
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        return text
    
    def _split_into_sections(self, content: str) -> List[str]:
        """페이지별로 섹션 분할"""
        # 페이지 구분자로 분할
        sections = re.split(r'---\n## 📄 페이지 \d+\n', content)
        
        # 각 섹션에 페이지 번호 다시 추가
        page_headers = re.findall(r'---\n## 📄 페이지 (\d+)\n', content)
        
        result = []
        for i, section in enumerate(sections[1:]):  # 첫 번째는 헤더이므로 제외
            if i < len(page_headers):
                result.append(f"## 📄 페이지 {page_headers[i]}\n{section}")
        
        return result
    
    def _clean_section(self, section: str) -> str:
        """각 섹션 정제"""
        lines = section.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 빈 줄 스킵
            if not line:
                continue
            
            # 너무 짧은 줄은 제거 (잡음)
            if len(line) < 3 and not line.isdigit():
                continue
            
            # 페이지 번호만 있는 줄 제거
            if re.match(r'^\d{1,3}$', line):
                continue
            
            # 정제된 줄 추가
            cleaned_lines.append(line)
        
        # 연속된 짧은 줄들을 하나로 합치기
        merged_lines = self._merge_short_lines(cleaned_lines)
        
        return '\n'.join(merged_lines)
    
    def _merge_short_lines(self, lines: List[str]) -> List[str]:
        """짧은 줄들을 의미 단위로 합치기"""
        merged = []
        buffer = []
        
        for line in lines:
            # 제목이나 헤더는 그대로 유지
            if line.startswith('#') or line.startswith('**['):
                if buffer:
                    merged.append(' '.join(buffer))
                    buffer = []
                merged.append(line)
            # 리스트 항목은 그대로 유지
            elif line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                if buffer:
                    merged.append(' '.join(buffer))
                    buffer = []
                merged.append(line)
            # 표 구분자는 그대로 유지
            elif '|' in line:
                if buffer:
                    merged.append(' '.join(buffer))
                    buffer = []
                merged.append(line)
            # 일반 텍스트는 버퍼에 추가
            else:
                if len(line) < 50:  # 짧은 줄은 버퍼에 추가
                    buffer.append(line)
                else:  # 긴 줄은 그대로 추가
                    if buffer:
                        merged.append(' '.join(buffer))
                        buffer = []
                    merged.append(line)
        
        # 남은 버퍼 처리
        if buffer:
            merged.append(' '.join(buffer))
        
        return merged
    
    def create_chunks(self, content: str) -> List[Dict]:
        """벡터 DB를 위한 청크 생성"""
        chunks = []
        sections = content.split('## 📄 페이지')
        
        for section in sections[1:]:  # 첫 번째는 빈 문자열
            # 페이지 번호 추출
            page_match = re.match(r' (\d+)\n', section)
            if not page_match:
                continue
            
            page_num = page_match.group(1)
            section_content = section[page_match.end():]
            
            # 섹션을 더 작은 청크로 분할 (500자 단위)
            chunk_size = 500
            for i in range(0, len(section_content), chunk_size):
                chunk_text = section_content[i:i+chunk_size]
                
                if len(chunk_text.strip()) > 50:  # 의미 있는 내용만
                    chunks.append({
                        'content': chunk_text.strip(),
                        'metadata': {
                            'page': int(page_num),
                            'chunk_start': i,
                            'chunk_end': min(i+chunk_size, len(section_content))
                        }
                    })
        
        return chunks

def main():
    # 경로 설정
    input_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_processed.md")
    output_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/samsung_esg_cleaned.md")
    
    # 정제 실행
    cleaner = MarkdownCleaner(input_path)
    cleaned_content = cleaner.clean()
    
    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 삼성전자 지속가능경영 보고서 2025 (정제됨)\n")
        f.write("*구조화되고 정제된 텍스트 - RAG 최적화*\n\n")
        f.write("---\n\n")
        f.write(cleaned_content)
    
    print(f"✅ 정제된 마크다운 저장: {output_path}")
    
    # 청크 생성
    chunks = cleaner.create_chunks(cleaned_content)
    print(f"📊 생성된 청크 수: {len(chunks)}")
    
    # 샘플 출력
    print("\n📝 청크 샘플:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n청크 {i+1} (페이지 {chunk['metadata']['page']}):")
        print(f"  {chunk['content'][:100]}...")
    
    return output_path, chunks

if __name__ == "__main__":
    output_file, chunks = main()
    print(f"\n🎯 다음 단계: 정제된 파일을 벡터 DB로 변환하세요.")