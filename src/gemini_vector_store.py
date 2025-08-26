from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
import os
import numpy as np

class GeminiVectorStore:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        
        # Use sentence-transformers for embeddings (free alternative)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize vector store
        self.vector_store = None
        self.client = None
        self.collection = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("samsung_sustainability")
        except Exception:
            self.collection = self.client.create_collection("samsung_sustainability")
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts using sentence-transformers"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        if not documents:
            return
        
        print(f"Adding {len(documents)} documents to vector store...")
        
        # Prepare data
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Get embeddings
        print("Generating embeddings...")
        embeddings = self._get_embeddings(texts)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            
            self.collection.add(
                embeddings=embeddings[i:batch_end],
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )
            
            print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        print(f"Vector store saved to {self.persist_directory}")
    
    def similarity_search(self, query: str, k: int = 8) -> List[Document]:
        """Search for similar documents"""
        if not self.collection:
            return []
        
        # Get query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Convert to Document objects
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                documents.append(Document(
                    page_content=doc,
                    metadata=metadata
                ))
        
        return documents
    
    def exists(self) -> bool:
        """Check if vector store exists and has data"""
        try:
            count = self.collection.count()
            return count > 0
        except:
            return False
    
    def clear(self):
        """Clear the vector store"""
        if self.collection:
            # Delete all documents
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
            print("Vector store cleared")