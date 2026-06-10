import os
import sys
from pathlib import Path
import streamlit as st

# Add src to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.graph import ShoppingAssistant

# --- Page Configuration ---
st.set_page_config(
    page_title="Shopping Assistant",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Glassmorphism & Dark Mode ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Glassmorphism Chat Containers */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* User Message distinct style */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* Chat Input Styling */
    .stChatInputContainer {
        padding-bottom: 2rem !important;
    }
    .stChatInputContainer textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1rem 1.5rem !important;
    }
    .stChatInputContainer textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Expander Styling (for traces) */
    .streamlit-expanderHeader {
        background: rgba(0,0,0,0.2) !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
    }
    .streamlit-expanderContent {
        background: rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
    }

    /* Hide standard header */
    header {visibility: hidden;}
    
    /* Main Title Styling */
    .main-title {
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #94a3b8;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Application Header ---
st.markdown('<h1 class="main-title">AI Shopping Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Powered by LangGraph & Qwen Multi-Agent System</p>', unsafe_allow_html=True)

# --- Backend Initialization ---
@st.cache_resource
def load_assistant():
    return ShoppingAssistant()

with st.spinner("Initializing AI Engine..."):
    assistant = load_assistant()

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi có thể giúp gì cho bạn hôm nay? (Ví dụ: 'Đơn hàng 1971 có được hoàn trả không?')"}
    ]

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "trace" in msg and msg["trace"]:
            with st.expander("🛠️ View Agent Traces (Behind the scenes)"):
                for t in msg["trace"]:
                    st.write(f"**Node:** `{t['node']}`")
                    st.json(t['output'])

# --- Handle User Input ---
if prompt := st.chat_input("Nhập câu hỏi của bạn vào đây..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process assistant response
    with st.chat_message("assistant"):
        with st.spinner("Suy nghĩ và phân tích..."):
            try:
                # Query LangGraph
                result = assistant.ask(question=prompt, rebuild_index=False)
                final_answer = result.get("final_answer", "Xin lỗi, tôi không thể trả lời lúc này.")
                trace = result.get("trace", [])
                
                st.write(final_answer)
                
                if trace:
                    with st.expander("🛠️ View Agent Traces (Behind the scenes)"):
                        for t in trace:
                            st.write(f"**Node:** `{t['node']}`")
                            st.json(t['output'])
                            
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_answer,
                    "trace": trace
                })
            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")
