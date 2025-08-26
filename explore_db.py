#!/usr/bin/env python3
"""
SQLite DB 브라우저 - 벡터 DB 내용을 자세히 탐색
"""

import sqlite3
import json
import sys
from pathlib import Path

DB_PATH = "/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db/chroma.sqlite3"

def explore_db():
    print("🗃️ ChromaDB SQLite 탐색기")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    while True:
        print("\n선택하세요:")
        print("1. 📊 전체 통계")
        print("2. 📝 문서 내용 보기")
        print("3. 🏷️ 메타데이터 보기")
        print("4. 🔍 키워드 검색")
        print("5. 📄 특정 페이지 문서들")
        print("6. 💾 원시 SQL 실행")
        print("0. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == "1":
            show_statistics(cursor)
        elif choice == "2":
            show_documents(cursor)
        elif choice == "3":
            show_metadata(cursor)
        elif choice == "4":
            search_content(cursor)
        elif choice == "5":
            show_page_documents(cursor)
        elif choice == "6":
            execute_sql(cursor)
        elif choice == "0":
            break
        else:
            print("잘못된 선택입니다.")
    
    conn.close()
    print("👋 탐색 완료!")

def show_statistics(cursor):
    print("\n📊 전체 통계")
    print("-" * 40)
    
    # 총 임베딩 수
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total_embeddings = cursor.fetchone()[0]
    print(f"총 임베딩 수: {total_embeddings}")
    
    # 컬렉션 정보
    cursor.execute("SELECT name, dimension FROM collections")
    collections = cursor.fetchall()
    for name, dimension in collections:
        print(f"컬렉션: {name}, 차원: {dimension}")
    
    # 페이지별 분포
    cursor.execute("""
        SELECT int_value as page, COUNT(*) as count 
        FROM embedding_metadata 
        WHERE key='page' 
        GROUP BY int_value 
        ORDER BY int_value 
        LIMIT 10
    """)
    pages = cursor.fetchall()
    print(f"\n페이지별 문서 수 (처음 10개):")
    for page, count in pages:
        print(f"  페이지 {page}: {count}개")

def show_documents(cursor):
    print("\n📝 문서 내용 보기")
    print("-" * 40)
    
    limit = input("몇 개 문서를 볼까요? (기본 3): ").strip() or "3"
    
    cursor.execute(f"""
        SELECT id, substr(c0, 1, 200) as preview, length(c0) as full_length
        FROM embedding_fulltext_search_content 
        LIMIT {limit}
    """)
    
    docs = cursor.fetchall()
    for doc_id, preview, length in docs:
        print(f"\n📄 문서 ID {doc_id} (총 {length} 문자):")
        print(f"   {preview}...")
        print("-" * 30)

def show_metadata(cursor):
    print("\n🏷️ 메타데이터 보기")
    print("-" * 40)
    
    doc_id = input("문서 ID를 입력하세요 (1-255): ").strip()
    
    cursor.execute("""
        SELECT key, string_value, int_value, float_value, bool_value
        FROM embedding_metadata 
        WHERE id = ?
    """, (doc_id,))
    
    metadata = cursor.fetchall()
    print(f"\n문서 {doc_id}의 메타데이터:")
    for key, str_val, int_val, float_val, bool_val in metadata:
        value = str_val or int_val or float_val or bool_val
        print(f"  {key}: {value}")

def search_content(cursor):
    print("\n🔍 키워드 검색")
    print("-" * 40)
    
    keyword = input("검색할 키워드: ").strip()
    
    cursor.execute("""
        SELECT id, substr(c0, 1, 150) as preview
        FROM embedding_fulltext_search_content 
        WHERE c0 LIKE ?
        LIMIT 5
    """, (f"%{keyword}%",))
    
    results = cursor.fetchall()
    print(f"\n'{keyword}' 검색 결과 ({len(results)}개):")
    for doc_id, preview in results:
        print(f"  📄 ID {doc_id}: {preview}...")
        print("-" * 30)

def show_page_documents(cursor):
    print("\n📄 특정 페이지 문서들")
    print("-" * 40)
    
    page = input("페이지 번호를 입력하세요: ").strip()
    
    cursor.execute("""
        SELECT m.id, substr(c.c0, 1, 200) as preview
        FROM embedding_metadata m
        JOIN embedding_fulltext_search_content c ON m.id = c.id
        WHERE m.key = 'page' AND m.int_value = ?
    """, (page,))
    
    results = cursor.fetchall()
    print(f"\n페이지 {page}의 문서들 ({len(results)}개):")
    for doc_id, preview in results:
        print(f"  📄 ID {doc_id}: {preview}...")
        print("-" * 30)

def execute_sql(cursor):
    print("\n💾 원시 SQL 실행")
    print("-" * 40)
    print("사용 가능한 테이블:", ", ".join([
        "embeddings", "embedding_metadata", 
        "embedding_fulltext_search_content", "collections"
    ]))
    
    sql = input("SQL 쿼리를 입력하세요: ").strip()
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if results:
            for row in results[:10]:  # 최대 10개만 표시
                print(f"  {row}")
            if len(results) > 10:
                print(f"  ... ({len(results) - 10}개 더)")
        else:
            print("결과 없음")
    except Exception as e:
        print(f"❌ SQL 오류: {e}")

if __name__ == "__main__":
    explore_db()