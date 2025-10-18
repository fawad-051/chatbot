# zaroori libraries import karein
import streamlit as st
import groq
import os
from dotenv import load_dotenv
import time
import random
from datetime import datetime

# .env file se API key load karein
load_dotenv()

# page ki settings
st.set_page_config(
    page_title="🤖 Advanced AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #4ECDC4;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 5px 18px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: white;
        color: #333;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 5px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #888;
        text-align: right;
        margin-top: 5px;
    }
    
    .stats-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #4ECDC4;
    }
    
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .stButton button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
    }
    
    .footer-signature {
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        margin-top: 10px;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# directly .env se API key lein
api_key = os.getenv("GROQ_API_KEY")

# agar API key nahi hai toh error
if not api_key:
    st.error("❌ API Key .env file mein nahi mili! Pehle .env file setup karein.")
    st.stop()

# session state initialize karein
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
    
if "chat_started" not in st.session_state:
    st.session_state.chat_started = datetime.now()

# main page layout
st.markdown('<h1 class="main-header">🤖 Advanced AI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Experience next-generation conversations powered by cutting-edge AI technology</p>', unsafe_allow_html=True)

# sidebar with enhanced design
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("### 🛠️ AI Settings")
    st.markdown("---")
    
    # model selection with icons
    model_options = {
        "⚡ Fast Model": "llama-3.1-8b-instant",
        "🧠 Smart Model": "qwen/qwen2.5-32b", 
        "🚀 Powerful Model": "openai/gpt-2-oss-120b"
    }
    
    selected_model_display = st.selectbox(
        "AI Model:",
        list(model_options.keys()),
        index=0,
        help="Apni pasand ka AI model choose karein"
    )
    selected_model = model_options[selected_model_display]
    
    # advanced settings in expander
    with st.expander("🎛️ Advanced Settings", expanded=True):
        # temperature slider with visual indicators
        st.markdown("**Creativity Level:**")
        temperature = st.slider(
            "Temperature:",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.1,
            help="0: Focused & Deterministic, 1: Creative & Random"
        )
        
        # show temperature indicator
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Focused" if temperature < 0.4 else "")
        with col2:
            st.caption("Balanced" if 0.4 <= temperature <= 0.7 else "")
        with col3:
            st.caption("Creative" if temperature > 0.7 else "")
        
        # max tokens slider  
        max_tokens = st.slider(
            "Response Length:",
            min_value=50,
            max_value=1000,
            value=300,
            step=50,
            help="Response ki maximum length"
        )
    
    st.markdown("---")
    
    # chat statistics
    st.markdown("### 📊 Chat Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.messages)//2)
    with col2:
        st.metric("Session Duration", f"{(datetime.now() - st.session_state.chat_started).seconds//60}m")
    
    st.markdown("---")
    
    # chat management
    st.markdown("### 💬 Chat Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_started = datetime.now()
            st.rerun()
    
    with col2:
        if st.button("📥 Export Chat", use_container_width=True):
            # Simple export functionality
            chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            st.download_button(
                label="Download Chat",
                data=chat_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # quick prompts
    st.markdown("### 💡 Quick Prompts")
    quick_prompts = [
        "Explain quantum computing simply",
        "Write a Python function for Fibonacci",
        "Suggest healthy breakfast ideas",
        "Plan a 3-day trip to Mumbai"
    ]
    
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state.quick_prompt = prompt
            st.rerun()
    
    # Add signature in sidebar
    st.markdown("---")
    st.markdown('<div class="footer-signature">Prepared by: Dr Fawad Hussain Paul</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# main content area
col1, col2 = st.columns([3, 1])

with col1:
    # chat container
    st.markdown("### 💬 Conversation")
    
    # handle quick prompt
    if "quick_prompt" in st.session_state:
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
    else:
        prompt = st.chat_input("Apna message yahan type karein...", key="chat_input")
    
    # display messages with enhanced UI
    chat_placeholder = st.empty()
    
    with chat_placeholder.container():
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
    
    # process user input
    if prompt:
        # user message dikhayein
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # assistant response with typing animation
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # typing animation
            typing_phrases = ["Thinking...", "Processing your query...", "Generating response..."]
            message_placeholder.info(random.choice(typing_phrases))
            
            try:
                # AI client banayein
                client = groq.Groq(api_key=api_key)
                
                # streaming response ke liye
                stream = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                
                # response stream karein with typing effect
                message_placeholder.empty()
                response_placeholder = st.empty()
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        # Simulate typing effect
                        response_placeholder.markdown(f'<div class="assistant-message">🤖 {full_response}▌</div>', unsafe_allow_html=True)
                        time.sleep(0.01)  # Smooth typing effect
                
                # Final response
                response_placeholder.markdown(f'<div class="assistant-message">🤖 {full_response}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error("❌ API se connect nahi ho paaya. Internet connection check karein.")
        
        # assistant ka response session state mein save karein
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()

with col2:
    # features and info panel
    st.markdown("### 🚀 Features")
    
    features = [
        {"icon": "⚡", "title": "Lightning Fast", "desc": "Advanced AI technology"},
        {"icon": "🔒", "title": "Secure", "desc": "Your data stays private"},
        {"icon": "🎯", "title": "Accurate", "desc": "Latest AI models"},
        {"icon": "💬", "title": "Multi-Topic", "desc": "Any subject expertise"}
    ]
    
    for feature in features:
        with st.container():
            st.markdown(f'<div class="feature-card">', unsafe_allow_html=True)
            st.markdown(f"### {feature['icon']}")
            st.markdown(f"**{feature['title']}**")
            st.markdown(f"<small>{feature['desc']}</small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    # model info card
    st.markdown("### ℹ️ Current Model")
    st.markdown(f'<div class="stats-card">', unsafe_allow_html=True)
    st.markdown(f"**{selected_model_display}**")
    st.markdown(f"Temp: {temperature}")
    st.markdown(f"Max Tokens: {max_tokens}")
    st.markdown('</div>', unsafe_allow_html=True)

# footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.markdown("**Built with ❤️ using Streamlit & Advanced AI**")
with footer_col2:
    st.markdown(f"**Active Session:** {st.session_state.chat_started.strftime('%H:%M')}")
with footer_col3:
    if st.session_state.messages:
        st.markdown(f"**Messages:** {len(st.session_state.messages)//2}")

# Add signature in main footer as well
st.markdown('<div class="footer-signature">Prepared by: Dr Fawad Hussain Paul</div>', unsafe_allow_html=True)