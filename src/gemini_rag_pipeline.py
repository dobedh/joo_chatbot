from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
import os
import google.generativeai as genai
from .hybrid_search import HybridSearch

class GeminiRAGPipeline:
    def __init__(self, vector_store, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.7):
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_output_tokens=2000
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create prompt template
        self.prompt_template = self._create_prompt_template()
        
        # Initialize hybrid search
        self.hybrid_search = HybridSearch(vector_store, dense_weight=0.6)
        
        # Initialize chain
        self.chain = None
        self._initialize_chain()
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for the chatbot"""
        template = """당신은 삼성전자 지속가능경영 보고서 전문가입니다. 
        제공된 문서 내용을 바탕으로 정확하고 도움이 되는 답변을 제공해주세요.
        
        답변 시 다음 사항을 준수해주세요:
        1. 제공된 문서 내용에 기반하여 답변하세요
        2. 정확한 정보를 제공하고, 불확실한 경우 그렇게 말씀해주세요
        3. 가능하면 구체적인 수치나 사례를 포함해주세요
        4. 답변은 명확하고 이해하기 쉽게 작성해주세요
        5. 한국어로 답변해주세요
        
        참고 문서:
        {context}
        
        대화 기록:
        {chat_history}
        
        질문: {question}
        
        답변:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
    
    def _create_retriever(self):
        """Create a custom retriever for our vector store"""
        class CustomRetriever:
            def __init__(self, vector_store):
                self.vector_store = vector_store
            
            def get_relevant_documents(self, query: str) -> List[Document]:
                return self.vector_store.similarity_search(query, k=5)
        
        return CustomRetriever(self.vector_store)
    
    def _initialize_chain(self):
        """Initialize the conversational retrieval chain"""
        if not self.vector_store or not self.vector_store.exists():
            raise ValueError("Vector store is not initialized or empty")
        
        # No longer need traditional retriever since we use hybrid search
        self.retriever = self._create_retriever()  # Keep for compatibility
    
    def query(self, question: str) -> Dict:
        """Process a query and return response with sources"""
        if not self.retriever:
            return {
                "answer": "시스템이 아직 초기화되지 않았습니다. PDF를 먼저 처리해주세요.",
                "sources": []
            }
        
        try:
            # Use hybrid search instead of simple retriever
            docs = self.hybrid_search.search(question, k=5)
            
            # 디버깅용: 검색된 문서 출력
            print(f"\n🔍 [디버깅] 검색 쿼리: {question}")
            print(f"📚 [디버깅] 검색된 {len(docs)}개 문서:")
            for i, doc in enumerate(docs, 1):
                print(f"  [{i}] 페이지 {doc.metadata.get('page', 'N/A')}, "
                      f"섹션: {doc.metadata.get('section', 'N/A')}, "
                      f"타입: {doc.metadata.get('chunk_type', 'N/A')}")
                print(f"      내용 미리보기: {doc.page_content[:100]}...")
            print("-" * 60)
            
            if not docs:
                return {
                    "answer": "관련 문서를 찾을 수 없습니다. 다른 질문을 해주세요.",
                    "sources": []
                }
            
            # Create context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Get chat history
            chat_history = ""
            if self.memory.chat_memory.messages:
                history_messages = []
                for msg in self.memory.chat_memory.messages[-4:]:  # Last 4 messages
                    role = "사용자" if msg.type == "human" else "어시스턴트"
                    history_messages.append(f"{role}: {msg.content}")
                chat_history = "\n".join(history_messages)
            
            # Format prompt
            prompt = self.prompt_template.format(
                context=context,
                chat_history=chat_history,
                question=question
            )
            
            # Get response from LLM
            response = self.llm.predict(prompt)
            
            # Update memory
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(response)
            
            # Format source documents with full metadata
            sources = []
            for i, doc in enumerate(docs, 1):
                sources.append({
                    "index": i,
                    "page": doc.metadata.get("page", "Unknown"),
                    "section": doc.metadata.get("section", "Unknown"),
                    "chunk_type": doc.metadata.get("chunk_type", "Unknown"),
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "keywords": doc.metadata.get("keywords", ""),
                    "metrics": doc.metadata.get("metrics", "")
                })
            
            return {
                "answer": response,
                "sources": sources
            }
        
        except Exception as e:
            return {
                "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                "sources": []
            }
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        messages = self.memory.chat_memory.messages
        history = []
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "question": messages[i].content,
                    "answer": messages[i + 1].content
                })
        
        return history