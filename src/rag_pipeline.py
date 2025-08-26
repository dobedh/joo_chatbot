from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import os

class RAGPipeline:
    def __init__(self, vector_store, model_name: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=2000
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create prompt template
        self.prompt_template = self._create_prompt_template()
        
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
        
        문서 내용:
        {context}
        
        대화 기록:
        {chat_history}
        
        질문: {question}
        
        답변:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
    
    def _initialize_chain(self):
        """Initialize the conversational retrieval chain"""
        if not self.vector_store.vector_store:
            raise ValueError("Vector store is not initialized")
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.vector_store.as_retriever(
                search_kwargs={"k": 5}
            ),
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": self.prompt_template}
        )
    
    def query(self, question: str) -> Dict:
        """Process a query and return response with sources"""
        if not self.chain:
            return {
                "answer": "시스템이 아직 초기화되지 않았습니다. PDF를 먼저 처리해주세요.",
                "source_documents": []
            }
        
        try:
            # Get response from chain
            response = self.chain({"question": question})
            
            # Format source documents
            sources = []
            for doc in response.get("source_documents", []):
                sources.append({
                    "page": doc.metadata.get("page", "Unknown"),
                    "content": doc.page_content[:200] + "..."  # Preview
                })
            
            return {
                "answer": response["answer"],
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