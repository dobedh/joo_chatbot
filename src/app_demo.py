import streamlit as st
from pathlib import Path
import sys
import os
import time
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

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
    
    /* Demo banner */
    .demo-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = True

# Demo responses based on keywords
def get_demo_response(question: str) -> dict:
    """Generate demo responses based on question keywords"""
    
    # Convert to lowercase for matching
    q_lower = question.lower()
    
    # ESG/지속가능경영 관련
    if any(word in q_lower for word in ["esg", "지속가능", "sustainability"]):
        return {
            "answer": """삼성전자의 지속가능경영은 다음 세 가지 핵심 축을 중심으로 추진되고 있습니다:

**1. 환경 (Environment)**
- 2050년 탄소중립 달성 목표
- 재생에너지 100% 전환 추진
- 순환경제 체계 구축

**2. 사회 (Social)**
- 협력사 상생 프로그램 운영
- 임직원 다양성 및 포용성 증진
- 지역사회 기여 활동 확대

**3. 거버넌스 (Governance)**
- 투명한 이사회 운영
- 윤리경영 강화
- 리스크 관리 체계 고도화

특히 2025년에는 반도체 사업장의 재생에너지 전환을 가속화하고, 제품 전 생애주기에 걸친 탄소 감축을 중점적으로 추진하고 있습니다.""",
            "sources": [
                {"page": 8, "content": "삼성전자는 환경경영을 넘어 지속가능경영으로 패러다임을 전환하고..."},
                {"page": 15, "content": "2050 탄소중립 목표 달성을 위한 로드맵을 수립하고 단계적으로..."}
            ]
        }
    
    # 탄소중립 관련
    elif any(word in q_lower for word in ["탄소", "carbon", "중립", "neutral", "배출"]):
        return {
            "answer": """삼성전자의 탄소중립 전략은 다음과 같습니다:

**2050 탄소중립 로드맵**
- 2030년까지: DX 부문 탄소중립 달성
- 2050년까지: 전 사업장 탄소중립 실현

**주요 실행 방안**
1. **재생에너지 전환**: 전 세계 사업장 재생에너지 100% 전환
2. **에너지 효율화**: 고효율 설비 도입 및 공정 개선
3. **탄소 포집**: CCUS 기술 개발 및 적용
4. **제품 혁신**: 저전력 반도체 및 에너지 효율 제품 개발

2024년 기준 재생에너지 전환율은 33%이며, 매년 15% 이상 확대 계획입니다.""",
            "sources": [
                {"page": 42, "content": "2050 탄소중립 달성을 위한 구체적인 실행 계획..."},
                {"page": 56, "content": "재생에너지 전환 현황 및 향후 계획..."}
            ]
        }
    
    # 순환경제 관련
    elif any(word in q_lower for word in ["순환", "재활용", "recycle", "circular", "폐기물"]):
        return {
            "answer": """삼성전자의 순환경제 활동은 다음과 같습니다:

**자원 순환 체계**
- 폐전자제품 회수 프로그램 운영 (2024년 450만 톤 회수)
- 재활용 소재 사용 확대 (플라스틱 20% 이상 재활용 소재 적용)
- 제품 수명 연장 프로그램

**폐기물 관리**
- 사업장 폐기물 재활용률 96% 달성
- 매립 제로화 추진 (2025년 목표)
- 유해물질 사용 최소화

**혁신 기술**
- 재생 플라스틱 사용 기술 개발
- 희귀금속 회수 기술 고도화
- 모듈형 설계로 수리 용이성 향상""",
            "sources": [
                {"page": 78, "content": "순환경제 실현을 위한 자원 효율성 극대화..."},
                {"page": 82, "content": "글로벌 회수 재활용 프로그램 운영 현황..."}
            ]
        }
    
    # 반도체 관련
    elif any(word in q_lower for word in ["반도체", "semiconductor", "chip", "메모리"]):
        return {
            "answer": """삼성전자 반도체 부문의 지속가능경영 활동:

**친환경 반도체 제조**
- 초저전력 반도체 개발 (전력 소비 30% 감축)
- 온실가스 저감 장치 운영 효율 99% 달성
- 수자원 재이용률 향상 (공업용수 재이용률 70%)

**그린 팹(Fab) 구축**
- 평택 캠퍼스: 재생에너지 100% 전환 추진
- 화성 캠퍼스: 에너지 효율 30% 개선
- 기흥 캠퍼스: 폐열 회수 시스템 구축

**공급망 관리**
- 협력사 탄소 감축 지원 프로그램
- 그린 파트너십 2030 이니셔티브""",
            "sources": [
                {"page": 95, "content": "반도체 제조 공정의 친환경 혁신..."},
                {"page": 103, "content": "그린 팹 구축을 통한 환경 영향 최소화..."}
            ]
        }
    
    # 일반적인 질문
    else:
        return {
            "answer": f"""'{question}'에 대한 답변입니다:

삼성전자는 지속가능한 미래를 위해 다양한 노력을 기울이고 있습니다. 

구체적인 내용은 다음과 같은 키워드로 질문해주세요:
- ESG 경영 전략
- 탄소중립 목표
- 순환경제 활동
- 재생에너지 전환
- 반도체 친환경 제조

더 자세한 정보가 필요하시면 구체적인 질문을 해주세요.""",
            "sources": [
                {"page": 3, "content": "삼성전자 지속가능경영 보고서 2025..."}
            ]
        }

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
    
    # Demo mode banner
    st.markdown("""
    <div class='demo-banner'>
    🎮 데모 모드 - 실제 API 연결 없이 체험해보세요!
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings (mobile-friendly)
    with st.sidebar:
        st.header("⚙️ 설정")
        
        if st.button("🔄 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.success("대화가 초기화되었습니다!")
            st.rerun()
        
        st.divider()
        
        # Model settings
        st.subheader("모델 설정")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
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
        - 반도체 친환경 제조
        
        **데모 모드 안내:**
        현재 데모 모드로 실행 중입니다.
        실제 PDF 처리 없이 미리 준비된 답변을 제공합니다.
        """)
    
    # Welcome message
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("""
            안녕하세요! 삼성전자 지속가능경영 AI 어시스턴트입니다. 👋
            
            저는 삼성전자의 ESG 활동과 지속가능경영에 대해 답변드릴 수 있습니다.
            
            **추천 질문:**
            - 삼성전자의 ESG 목표는 무엇인가요?
            - 탄소중립 달성 계획을 알려주세요
            - 순환경제 활동에 대해 설명해주세요
            """)
    
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
            # Simulate thinking time
            with st.spinner("답변을 생성하는 중..."):
                time.sleep(1.5)  # Simulate processing time
                response = get_demo_response(prompt)
            
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
    
    # Mobile-friendly footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0; color: #666; font-size: 0.8rem;'>
    Samsung Sustainability Report AI Assistant v1.0 (Demo Mode)
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()