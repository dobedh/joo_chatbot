from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

class VectorStore:
    def __init__(self, persist_directory: str, embedding_model: str = "text-embedding-3-small"):
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize or load vector store
        self.vector_store = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        self.vector_store = Chroma(
            collection_name="samsung_sustainability",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        if not documents:
            return
        
        # Add documents in batches
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.vector_store.add_documents(batch)
            print(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        # Persist the vector store
        self.vector_store.persist()
        print(f"Vector store persisted to {self.persist_directory}")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k
        )
        
        # Filter by relevance score
        filtered_results = [
            doc for doc, score in results if score > 0.5
        ]
        
        return filtered_results
    
    def exists(self) -> bool:
        """Check if vector store exists"""
        return os.path.exists(self.persist_directory) and \
               len(os.listdir(self.persist_directory)) > 0
    
    def clear(self):
        """Clear the vector store"""
        if self.vector_store:
            # Delete the collection
            self.vector_store.delete_collection()
            print("Vector store cleared")