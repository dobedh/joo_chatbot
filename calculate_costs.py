#!/usr/bin/env python3
"""
RAG 시스템 비용 계산
한 번의 검색 + 응답 생성 시 발생하는 비용 분석
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.korean_vector_store import KoreanVectorStore
from src.hybrid_search import HybridSearch
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def calculate_embedding_cost():
    """임베딩 비용 계산 (ko-sroberta-multitask 사용)"""
    print("\n📊 임베딩 비용 분석")
    print("-" * 50)
    
    # ko-sroberta-multitask는 로컬 모델이므로 비용 없음
    print("✅ 임베딩 모델: ko-sroberta-multitask (로컬)")
    print("💰 비용: $0 (무료 - 로컬 실행)")
    
    return 0


def calculate_search_cost():
    """벡터 검색 비용 계산"""
    print("\n🔍 벡터 검색 비용 분석")
    print("-" * 50)
    
    # ChromaDB는 로컬 벡터 DB이므로 비용 없음
    print("✅ 벡터 DB: ChromaDB (로컬)")
    print("💰 비용: $0 (무료 - 로컬 실행)")
    
    return 0


def calculate_llm_cost(query: str = "인권 교육을 몇프로가 받았어?"):
    """LLM 응답 생성 비용 계산"""
    print("\n🤖 LLM 비용 분석 (Google Gemini)")
    print("-" * 50)
    
    # 벡터 스토어에서 실제 컨텍스트 가져오기
    vector_store = KoreanVectorStore(persist_directory="data/chroma_db")
    results = vector_store.similarity_search(query, k=5)
    
    # 컨텍스트 구성
    context_texts = []
    for doc in results:
        context_texts.append(doc.page_content)
    
    full_context = "\n\n".join(context_texts)
    
    # 프롬프트 구성
    system_prompt = """당신은 삼성전자의 ESG 전문가입니다. 
    제공된 정보를 바탕으로 정확하고 신뢰할 수 있는 답변을 제공하세요.
    답변은 간결하고 명확하게 작성하되, 중요한 세부사항은 포함하세요."""
    
    user_prompt = f"""다음 정보를 참고하여 질문에 답변해주세요:

<컨텍스트>
{full_context}
</컨텍스트>

질문: {query}

답변:"""
    
    # 전체 프롬프트
    full_prompt = system_prompt + "\n\n" + user_prompt
    
    # 토큰 수 계산 (근사치)
    # Gemini는 문자 수 기반으로 대략 계산
    input_chars = len(full_prompt)
    avg_output_chars = 500  # 평균 응답 길이
    
    # Gemini 2.0 Flash 가격 (2024년 기준)
    # Input: $0.075 per 1M characters
    # Output: $0.30 per 1M characters
    
    input_cost = (input_chars / 1_000_000) * 0.075
    output_cost = (avg_output_chars / 1_000_000) * 0.30
    
    print(f"📝 쿼리: {query}")
    print(f"📄 컨텍스트 크기: {len(full_context):,} 문자")
    print(f"📥 입력 프롬프트 크기: {input_chars:,} 문자")
    print(f"📤 예상 출력 크기: {avg_output_chars:,} 문자")
    print(f"\n💵 Gemini 2.0 Flash 가격:")
    print(f"   - 입력: $0.075 / 1M 문자")
    print(f"   - 출력: $0.30 / 1M 문자")
    print(f"\n💰 예상 비용:")
    print(f"   - 입력 비용: ${input_cost:.6f}")
    print(f"   - 출력 비용: ${output_cost:.6f}")
    print(f"   - 총 LLM 비용: ${input_cost + output_cost:.6f}")
    
    # 실제 API 호출 시뮬레이션
    print(f"\n🔄 실제 API 호출 시뮬레이션...")
    
    # API 설정
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    try:
        # 실제 응답 생성
        response = model.generate_content(full_prompt)
        actual_output_chars = len(response.text)
        actual_output_cost = (actual_output_chars / 1_000_000) * 0.30
        
        print(f"✅ 실제 응답 크기: {actual_output_chars:,} 문자")
        print(f"💰 실제 출력 비용: ${actual_output_cost:.6f}")
        print(f"💰 실제 총 비용: ${input_cost + actual_output_cost:.6f}")
        
        return input_cost + actual_output_cost
        
    except Exception as e:
        print(f"⚠️ API 호출 실패 (예상 비용만 표시): {e}")
        return input_cost + output_cost


def calculate_total_cost_per_query():
    """쿼리당 총 비용 계산"""
    print("\n" + "=" * 60)
    print("💰 RAG 시스템 쿼리당 총 비용 분석")
    print("=" * 60)
    
    # 각 구성 요소 비용
    embedding_cost = calculate_embedding_cost()
    search_cost = calculate_search_cost()
    llm_cost = calculate_llm_cost()
    
    total_cost = embedding_cost + search_cost + llm_cost
    
    print("\n" + "=" * 60)
    print("📊 비용 요약")
    print("=" * 60)
    print(f"1. 임베딩 비용: ${embedding_cost:.6f}")
    print(f"2. 검색 비용: ${search_cost:.6f}")
    print(f"3. LLM 비용: ${llm_cost:.6f}")
    print(f"\n🎯 쿼리당 총 비용: ${total_cost:.6f}")
    
    # 월간 예상 비용
    queries_per_day = 100
    queries_per_month = queries_per_day * 30
    monthly_cost = total_cost * queries_per_month
    
    print(f"\n📅 월간 예상 비용 (일 {queries_per_day}회 사용 기준):")
    print(f"   - 월 {queries_per_month:,}회 쿼리")
    print(f"   - 월 예상 비용: ${monthly_cost:.2f}")
    
    # 비용 절감 방안
    print(f"\n💡 비용 절감 방안:")
    print("1. ✅ 로컬 임베딩 모델 사용 (현재 적용)")
    print("2. ✅ 로컬 벡터 DB 사용 (현재 적용)")
    print("3. 📌 Gemini Flash 모델 사용 (현재 적용 - 가장 저렴한 옵션)")
    print("4. 💾 응답 캐싱으로 중복 쿼리 비용 절감 가능")
    print("5. 📝 컨텍스트 크기 최적화 (k=5 → k=3으로 축소 가능)")
    
    return total_cost


def compare_with_other_models():
    """다른 LLM 모델과 비용 비교"""
    print("\n" + "=" * 60)
    print("🔄 다른 LLM 모델과 비용 비교")
    print("=" * 60)
    
    # 평균 입력/출력 크기 (문자)
    avg_input = 5000
    avg_output = 500
    
    models = [
        {
            "name": "Gemini 2.0 Flash (현재)",
            "input_price": 0.075 / 1_000_000,
            "output_price": 0.30 / 1_000_000,
            "unit": "문자"
        },
        {
            "name": "GPT-4o mini",
            "input_price": 0.15 / 1_000_000,  # per token, ~4 chars per token
            "output_price": 0.60 / 1_000_000,
            "unit": "토큰",
            "char_per_token": 4
        },
        {
            "name": "Claude 3 Haiku",
            "input_price": 0.25 / 1_000_000,
            "output_price": 1.25 / 1_000_000,
            "unit": "토큰",
            "char_per_token": 4
        },
        {
            "name": "GPT-3.5 Turbo",
            "input_price": 0.50 / 1_000_000,
            "output_price": 1.50 / 1_000_000,
            "unit": "토큰",
            "char_per_token": 4
        }
    ]
    
    print(f"📊 기준: 입력 {avg_input:,}자, 출력 {avg_output:,}자\n")
    
    for model in models:
        if model["unit"] == "토큰":
            # 토큰 기반 모델은 문자를 토큰으로 변환
            input_tokens = avg_input / model["char_per_token"]
            output_tokens = avg_output / model["char_per_token"]
            input_cost = input_tokens * model["input_price"]
            output_cost = output_tokens * model["output_price"]
        else:
            # 문자 기반 모델
            input_cost = avg_input * model["input_price"]
            output_cost = avg_output * model["output_price"]
        
        total = input_cost + output_cost
        
        print(f"🤖 {model['name']}:")
        print(f"   입력: ${input_cost:.6f}")
        print(f"   출력: ${output_cost:.6f}")
        print(f"   총액: ${total:.6f}")
        
        if model['name'] == "Gemini 2.0 Flash (현재)":
            print(f"   ✅ 현재 선택된 모델")
        print()


def main():
    """메인 실행 함수"""
    print("\n🚀 RAG 시스템 비용 분석 시작\n")
    
    # 1. 쿼리당 총 비용 계산
    cost_per_query = calculate_total_cost_per_query()
    
    # 2. 다른 모델과 비교
    compare_with_other_models()
    
    print("\n✅ 비용 분석 완료!\n")
    
    # 최종 요약
    print("📌 핵심 요약:")
    print(f"- 쿼리당 비용: ${cost_per_query:.6f} (약 {cost_per_query * 1400:.2f}원)")
    print(f"- 주요 비용: LLM API 호출 (Gemini 2.0 Flash)")
    print(f"- 절감 요소: 로컬 임베딩 + 로컬 벡터 DB 사용")
    print(f"- 추천: 현재 구성이 가장 비용 효율적")


if __name__ == "__main__":
    main()