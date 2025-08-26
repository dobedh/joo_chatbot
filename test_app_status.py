#!/usr/bin/env python3
"""
앱 상태 확인 스크립트
"""

import requests
import sys
from pathlib import Path

def check_app_status():
    """Streamlit 앱 상태 확인"""
    
    print("=" * 60)
    print("🔍 삼성전자 ESG 챗봇 상태 확인")
    print("=" * 60)
    
    # 1. 앱 실행 확인
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit 앱 실행 중")
        else:
            print(f"⚠️ 앱 응답 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ 앱 접속 실패: {e}")
        return False
    
    # 2. 벡터 DB 확인
    db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
    if db_path.exists():
        print("✅ 한국어 벡터 DB 존재")
        
        # ChromaDB 파일 확인
        sqlite_file = db_path / "chroma.sqlite3"
        if sqlite_file.exists():
            size_mb = sqlite_file.stat().st_size / (1024 * 1024)
            print(f"   - DB 크기: {size_mb:.1f} MB")
    else:
        print("❌ 벡터 DB 없음")
    
    # 3. 필수 파일 확인
    required_files = [
        "src/app_gemini.py",
        "src/korean_vector_store.py",
        "src/gemini_rag_pipeline.py",
        "data/samsung_esg_advanced.md"
    ]
    
    print("\n📁 필수 파일 확인:")
    all_exist = True
    for file in required_files:
        file_path = Path(f"/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/{file}")
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            all_exist = False
    
    # 4. 최종 상태
    print("\n" + "=" * 60)
    if all_exist:
        print("🎉 시스템 정상 작동 중!")
        print("\n📱 접속 방법:")
        print("   - 브라우저에서: http://localhost:8501")
        print("   - 모바일에서: 같은 네트워크에서 IP:8501")
        print("\n💬 테스트 질문:")
        print("   - '2024년 매출은?'")
        print("   - 'DX부문 탄소중립 목표는?'")
        print("   - 'DS부문 재생에너지 전환율은?'")
        return True
    else:
        print("⚠️ 일부 구성 요소 누락")
        return False

if __name__ == "__main__":
    success = check_app_status()
    sys.exit(0 if success else 1)