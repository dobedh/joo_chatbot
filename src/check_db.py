#!/usr/bin/env python3
"""Check ChromaDB contents"""

import chromadb
from pathlib import Path

db_path = Path("/Users/donghyunkim/Desktop/joo_project/samsung_chatbot/data/chroma_db_korean")

# Connect to ChromaDB
client = chromadb.PersistentClient(path=str(db_path))

# List all collections
collections = client.list_collections()
print(f"Collections in DB: {[col.name for col in collections]}")

for col in collections:
    print(f"\nCollection: {col.name}")
    print(f"  Count: {col.count()}")
    
    # Get sample data
    data = col.get(limit=2)
    if data['ids']:
        print(f"  Sample IDs: {data['ids'][:2]}")
        if data.get('documents'):
            print(f"  Sample doc: {data['documents'][0][:100]}...")