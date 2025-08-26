import streamlit as st
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import *
from src.korean_vector_store import KoreanVectorStore
from src.gemini_rag_pipeline import GeminiRAGPipeline

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
        color: #333333 !important;
    }
    
    .source-box strong {
        color: #000000 !important;
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
    
    /* Powered by banner */
    .powered-by {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 25%, #fbbc05 50%, #ea4335 75%);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-size: 0.9em;
        font-weight: bold;
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
        if not GOOGLE_API_KEY:
            st.error("⚠️ Google API 키가 설정되지 않았습니다.")
            st.info("🔗 Streamlit Cloud에서는 Settings > Secrets에서 GOOGLE_API_KEY를 설정하세요.")
            return None, None
        
        # Initialize Korean vector store
        korean_db_path = str(Path(CHROMA_PERSIST_DIRECTORY).parent / "chroma_db_korean")
        
        # Check if DB exists, if not initialize it
        db_path = Path(korean_db_path)
        if not db_path.exists() or len(list(db_path.iterdir())) == 0:
            st.warning("⏳ 첫 실행입니다. 벡터 DB를 초기화 중...")
            
            # Import initialization function
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from init_db import initialize_db
            
            # Initialize DB
            success = initialize_db()
            if not success:
                st.error("❌ DB 초기화 실패")
                return None, None
            st.success("✅ 벡터 DB 초기화 완료!")
        
        vector_store = KoreanVectorStore(
            persist_directory=korean_db_path
        )
        
        # Check if Korean vector store exists
        if not vector_store.exists():
            st.error("❌ 한국어 벡터 DB 로드 실패")
            return None, None
        else:
            st.success("✅ 한국어 최적화 벡터 DB 로드 완료!")
        
        # Initialize RAG pipeline
        rag_pipeline = GeminiRAGPipeline(
            vector_store=vector_store,
            model_name=LLM_MODEL,
            temperature=TEMPERATURE
        )
        
        return vector_store, rag_pipeline
    
    except Exception as e:
        st.error(f"❌ 시스템 초기화 중 오류 발생: {str(e)}")
        st.info("🔍 API 키가 올바르게 설정되었는지 확인해주세요.")
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
    
    # Powered by banner
    st.markdown("""
    <div class='powered-by'>
    🤖 Powered by Google Gemini AI & ChromaDB
    </div>
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
        
        # System status
        st.divider()
        st.subheader("📊 시스템 상태")
        
        if st.session_state.initialized:
            st.success("✅ RAG 시스템 활성화")
            if st.session_state.vector_store and st.session_state.vector_store.exists():
                doc_count = st.session_state.vector_store.collection.count()
                st.info(f"📚 문서 청크: {doc_count}개")
        else:
            st.warning("⚠️ 시스템 초기화 필요")
        
        st.divider()
        
        # About
        st.subheader("ℹ️ 정보")
        st.markdown("""
        이 챗봇은 삼성전자 2025 지속가능경영 보고서를 기반으로 답변합니다.
        
        **사용 가능한 질문 예시:**
        - DX부문 탄소중립 목표는?
        - DS부문 반도체 사업 현황
        - 2024년 매출 실적
        - 재생에너지 전환율
        - CEO 메시지 요약
        
        **기술 스택:**
        - 🤖 Google Gemini 1.5 Flash
        - 🇰🇷 ko-sroberta-multitask (한국어 특화)
        - 🔍 ChromaDB 벡터 검색
        - 📱 모바일 최적화 UI
        """)
    
    # Chat interface
    if st.session_state.initialized:
        # Welcome message
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.markdown("""
                안녕하세요! 삼성전자 지속가능경영 AI 어시스턴트입니다. 👋
                
                저는 삼성전자의 ESG 활동과 지속가능경영에 대해 **실제 보고서 기반**으로 답변드립니다.
                
                **추천 질문:**
                - DX부문의 2030년 탄소중립 목표는?
                - 2024년 매출과 영업이익 실적은?
                - DS부문 반도체 사업의 재생에너지 전환율은?
                - ESG 전략과 주요 성과를 알려주세요
                """)
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources if available
                if "sources" in message and message["sources"]:
                    with st.expander(f"📚 출처 보기 (검색된 {len(message['sources'])}개 문서)"):
                        st.markdown("**🔍 실제 사용된 문서들:**")
                        for source in message["sources"]:
                            st.markdown(f"""
                            <div class='source-box' style='margin-bottom: 15px; color: #333333;'>
                            <strong style='color: #000000;'>[문서 {source.get('index', '')}]</strong> 
                            <span style='color: #555555;'>📄 페이지 {source.get('page', 'N/A')} | 
                            📂 섹션: {source.get('section', 'N/A')} | 
                            📝 타입: {source.get('chunk_type', 'N/A')}</span><br><br>
                            <strong style='color: #000000;'>내용:</strong><br>
                            <span style='color: #333333;'>{source.get('content', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if source.get('keywords'):
                                st.caption(f"🏷️ 키워드: {source['keywords']}")
                            if source.get('metrics'):
                                st.caption(f"📊 수치: {source['metrics']}")
                            st.divider()
        
        # Chat input
        if prompt := st.chat_input("질문을 입력하세요...", key="chat_input"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("문서를 검색하고 답변을 생성하는 중..."):
                    response = st.session_state.rag_pipeline.query(prompt)
                    
                    st.markdown(response["answer"])
                    
                    # Show sources with detailed information
                    if response.get("sources"):
                        with st.expander(f"📚 출처 보기 (검색된 {len(response['sources'])}개 문서)"):
                            st.markdown("**🔍 실제 사용된 문서들:**")
                            for source in response["sources"]:
                                st.markdown(f"""
                                <div class='source-box' style='margin-bottom: 15px; color: #333333;'>
                                <strong style='color: #000000;'>[문서 {source.get('index', '')}]</strong> 
                                <span style='color: #555555;'>📄 페이지 {source.get('page', 'N/A')} | 
                                📂 섹션: {source.get('section', 'N/A')} | 
                                📝 타입: {source.get('chunk_type', 'N/A')}</span><br><br>
                                <strong style='color: #000000;'>내용:</strong><br>
                                <span style='color: #333333;'>{source.get('content', '')}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 키워드와 메트릭이 있으면 표시
                                if source.get('keywords'):
                                    st.caption(f"🏷️ 키워드: {source['keywords']}")
                                if source.get('metrics'):
                                    st.caption(f"📊 수치: {source['metrics']}")
                                st.divider()
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
    else:
        st.error("⚠️ 시스템이 초기화되지 않았습니다.")
        
        if not GOOGLE_API_KEY:
            st.markdown("""
            ### 🔑 Google API 키 설정이 필요합니다
            
            1. **https://makersuite.google.com/** 접속
            2. **"Get API Key"** 클릭
            3. 무료 API 키 생성
            4. `.env` 파일에 `GOOGLE_API_KEY=your_key_here` 추가
            5. 앱 재시작
            """)
    
    # Mobile-friendly footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0; color: #666; font-size: 0.8rem;'>
    Samsung Sustainability Report AI Assistant v2.0<br>
    Powered by Google Gemini AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()