#!/usr/bin/env python3
"""
Gemini 2.0 Flash 모델 테스트
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def test_gemini_2():
    """Gemini 2.0 Flash 테스트"""
    
    print("=" * 60)
    print("🚀 Gemini 2.0 Flash 모델 테스트")
    print("=" * 60)
    
    try:
        # Gemini 2.0 Flash 초기화
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_output_tokens=500
        )
        
        # 간단한 테스트
        print("\n📝 테스트 질문: '안녕하세요. 한국어를 이해하시나요?'")
        
        response = llm.invoke("안녕하세요. 한국어를 이해하시나요? 짧게 답해주세요.")
        
        print(f"\n✅ 응답: {response.content}")
        
        # 모델 정보
        print(f"\n📊 모델 정보:")
        print(f"   - 모델명: gemini-2.0-flash-exp")
        print(f"   - 상태: 정상 작동")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_2()
    
    if success:
        print("\n✅ Gemini 2.0 Flash 모델 정상 작동!")
        print("💡 이제 챗봇에서 사용할 수 있습니다.")
    else:
        print("\n⚠️ 모델 테스트 실패")
        print("API 키와 할당량을 확인하세요.")