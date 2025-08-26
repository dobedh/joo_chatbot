import streamlit as st
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import *
from src.pdf_processor import PDFProcessor
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline

# Mobile-optimized CSS
def load_mobile_css():
    st.markdown("""
    <style>
    /* Mobile responsive design */
    @media (max-width: 768px) {
        .stApp {
            padding: 0 !important;
        }
        
        .main > div {
            padding: 1rem 0.5rem !important;
        }
        
        /* Chat container */
        .stChatFloatingInputContainer {
            bottom: 0 !important;
            padding: 0.5rem !important;
        }
        
        /* Messages */
        .stChatMessage {
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Input box */
        .stTextInput > div > div > input {
            font-size: 16px !important; /* Prevent zoom on iOS */
        }
        
        /* Buttons */
        .stButton > button {
            width: 100% !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
        }
        
        /* Sidebar toggle */
        .css-1aumxhk {
            padding: 0.5rem !important;
        }
    }
    
    /* Desktop and mobile shared styles */
    .stApp {
        max-width: 100%;
    }
    
    /* Chat messages styling */
    .user-message {
        background-color: #E3F2FD;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background-color: #F5F5F5;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    /* Source citations */
    .source-box {
        background-color: #FFF9C4;
        border-left: 4px solid #FFC107;
        padding: 8px 12px;
        margin: 8px 0;
        font-size: 0.9em;
        border-radius: 4px;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
        animation: loading 1.4s infinite;
    }
    
    @keyframes loading {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Improve mobile viewport */
    @viewport {
        width: device-width;
        initial-scale: 1;
        maximum-scale: 1;
        user-scalable: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    
    if "rag_pipeline" not in st.session_state:
        st.session_state.rag_pipeline = None
    
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

# Initialize the system
@st.cache_resource
def initialize_system():
    """Initialize vector store and RAG pipeline"""
    try:
        # Check if API key is set
        if not OPENAI_API_KEY:
            st.error("⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return None, None
        
        # Initialize vector store
        vector_store = VectorStore(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_model=EMBEDDING_MODEL
        )
        
        # Check if vector store exists, if not process PDF
        if not vector_store.exists():
            st.info("📚 PDF를 처리하고 있습니다. 잠시만 기다려주세요...")
            
            # Process PDF
            processor = PDFProcessor(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
            
            if PDF_PATH.exists():
                chunks = processor.process_pdf(PDF_PATH)
                vector_store.add_documents(chunks)
                st.success("✅ PDF 처리가 완료되었습니다!")
            else:
                st.error(f"❌ PDF 파일을 찾을 수 없습니다: {PDF_PATH}")
                return None, None
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            model_name=LLM_MODEL,
            temperature=TEMPERATURE
        )
        
        return vector_store, rag_pipeline
    
    except Exception as e:
        st.error(f"❌ 시스템 초기화 중 오류 발생: {str(e)}")
        return None, None

# Main app
def main():
    st.set_page_config(
        page_title="삼성전자 지속가능경영 AI 어시스턴트",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load mobile CSS
    load_mobile_css()
    
    # Initialize session state
    init_session_state()
    
    # Title with mobile-friendly size
    st.markdown("""
    <h1 style='text-align: center; font-size: 1.5rem; padding: 1rem 0;'>
    🌱 삼성전자 지속가능경영 AI 어시스턴트
    </h1>
    """, unsafe_allow_html=True)
    
    # Initialize system if not already done
    if not st.session_state.initialized:
        with st.spinner("시스템을 초기화하는 중..."):
            vector_store, rag_pipeline = initialize_system()
            if vector_store and rag_pipeline:
                st.session_state.vector_store = vector_store
                st.session_state.rag_pipeline = rag_pipeline
                st.session_state.initialized = True
                st.rerun()
    
    # Sidebar for settings (mobile-friendly)
    with st.sidebar:
        st.header("⚙️ 설정")
        
        if st.button("🔄 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.rag_pipeline:
                st.session_state.rag_pipeline.clear_memory()
            st.success("대화가 초기화되었습니다!")
            st.rerun()
        
        st.divider()
        
        # Model settings
        st.subheader("모델 설정")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=TEMPERATURE,
            step=0.1,
            help="낮을수록 일관된 답변, 높을수록 창의적인 답변"
        )
        
        st.divider()
        
        # About
        st.subheader("ℹ️ 정보")
        st.markdown("""
        이 챗봇은 삼성전자 2025 지속가능경영 보고서를 기반으로 답변합니다.
        
        **사용 가능한 질문 예시:**
        - ESG 목표는 무엇인가요?
        - 탄소중립 계획을 알려주세요
        - 순환경제 활동은?
        """)
    
    # Chat interface
    if st.session_state.initialized:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("📚 출처 보기"):
                        for source in message["sources"]:
                            st.markdown(f"""
                            <div class='source-box'>
                            📄 페이지 {source['page']}<br>
                            {source['content']}
                            </div>
                            """, unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("질문을 입력하세요...", key="chat_input"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("답변을 생성하는 중..."):
                    response = st.session_state.rag_pipeline.query(prompt)
                    
                    st.markdown(response["answer"])
                    
                    # Show sources
                    if response.get("sources"):
                        with st.expander("📚 출처 보기"):
                            for source in response["sources"]:
                                st.markdown(f"""
                                <div class='source-box'>
                                📄 페이지 {source['page']}<br>
                                {source['content']}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
    else:
        st.error("⚠️ 시스템이 초기화되지 않았습니다. 페이지를 새로고침해주세요.")
    
    # Mobile-friendly footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0; color: #666; font-size: 0.8rem;'>
    Samsung Sustainability Report AI Assistant v1.0
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()