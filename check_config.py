#!/usr/bin/env python3
"""
현재 설정 확인
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

print("=" * 60)
print("🔍 현재 설정 확인")
print("=" * 60)

# API 키 확인 (마지막 4자리만 표시)
api_key = os.getenv("GOOGLE_API_KEY", "NOT SET")
if api_key != "NOT SET":
    print(f"✅ API Key: ...{api_key[-4:]}")
else:
    print("❌ API Key: NOT SET")

# 모델 설정
print(f"\n📊 모델 설정:")
print(f"   LLM_MODEL: {os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')}")

# config.py 직접 확인
sys.path.append(str(Path(__file__).parent))
from src.config import LLM_MODEL, GOOGLE_API_KEY

print(f"\n📁 config.py에서 로드:")
print(f"   LLM_MODEL: {LLM_MODEL}")
print(f"   API Key: ...{GOOGLE_API_KEY[-4:] if GOOGLE_API_KEY else 'NONE'}")

# Vector DB 경로
db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")
if db_path.exists():
    print(f"\n✅ Vector DB 존재: {db_path}")
    sqlite_file = db_path / "chroma.sqlite3"
    if sqlite_file.exists():
        size_mb = sqlite_file.stat().st_size / (1024 * 1024)
        print(f"   크기: {size_mb:.1f} MB")
else:
    print(f"\n❌ Vector DB 없음")

print("\n" + "=" * 60)