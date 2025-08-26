from typing import List, Dict
import pypdf
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import re

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """Extract text from PDF with metadata"""
        documents = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                
                # Clean text
                text = self._clean_text(text)
                
                if text.strip():
                    documents.append({
                        'content': text,
                        'metadata': {
                            'page': page_num,
                            'source': pdf_path.name,
                            'total_pages': len(pdf_reader.pages)
                        }
                    })
        
        return documents
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Korean
        text = re.sub(r'[^\w\s가-힣.,!?;:\-()]', '', text)
        return text.strip()
    
    def create_chunks(self, documents: List[Dict]) -> List[Document]:
        """Split documents into chunks"""
        all_chunks = []
        
        for doc in documents:
            # Create LangChain Document
            langchain_doc = Document(
                page_content=doc['content'],
                metadata=doc['metadata']
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([langchain_doc])
            
            # Update metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['chunk_total'] = len(chunks)
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """Complete PDF processing pipeline"""
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text
        documents = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(documents)} pages")
        
        # Create chunks
        chunks = self.create_chunks(documents)
        print(f"Created {len(chunks)} chunks")
        
        return chunks