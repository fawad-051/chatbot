# zaroori libraries import karein
import streamlit as st
import groq
import os
from dotenv import load_dotenv
import time
import random
from datetime import datetime
import tempfile
import PyPDF2
import docx
import pandas as pd

# .env file se API key load karein (local development ke liye)
load_dotenv()

# page ki settings
st.set_page_config(
    page_title="🤖 Advanced AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API key get karne ka improved method
def get_api_key():
    # Pehle Streamlit secrets check karein
    try:
        if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
            return st.secrets['GROQ_API_KEY']
    except:
        pass
    
    # Phir environment variable check karein
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key
    
    # Agar kahi se bhi nahi mili toh
    return None

# API key get karein
api_key = get_api_key()

# agar API key nahi hai toh error with guidance
if not api_key:
    st.error("""
    ❌ API Key nahi mili!
    
    **Solution Steps:**
    
    1. **Groq API Key Banayein:**
       - https://console.groq.com par jayein
       - Sign up/Login karein
       - API key generate karein
    
    2. **Deployment Settings:**
       - Streamlit app ke settings mein jayein
       - "Secrets" section mein yeh add karein:
         ```
         GROQ_API_KEY = "apna_actual_api_key_yahan_dalein"
         ```
    
    3. **Local Testing:**
       - Project folder mein `.env` file banayein
       - Usmein `GROQ_API_KEY=apna_actual_api_key` add karein
    """)
    
    # Additional help links
    st.markdown("""
    **Helpful Links:**
    - [Groq API Console](https://console.groq.com)
    - [Streamlit Secrets Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
    """)
    
    st.stop()

# ... (baaki ka code waisa hi rahega)

# session state initialize karein
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
    
if "chat_started" not in st.session_state:
    st.session_state.chat_started = datetime.now()

if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

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
    
    # File upload section
    st.markdown("### 📁 File Attachment")
    uploaded_file = st.file_uploader(
        "File attach karein",
        type=['pdf', 'txt', 'docx', 'csv'],
        help="PDF, TXT, DOCX, ya CSV files upload karein"
    )
    
    if uploaded_file is not None:
        with st.spinner("File process ho rahi hai..."):
            file_content, file_name = process_uploaded_file(uploaded_file)
            st.session_state.uploaded_file_content = file_content
            st.session_state.uploaded_file_name = file_name
            
        st.success(f"✅ {file_name} successfully loaded!")
        
        # File info display
        st.markdown(f'<div class="file-info-card">', unsafe_allow_html=True)
        st.markdown(f"**📄 {file_name}**")
        if len(str(file_content)) > 100:
            st.markdown(f"Content preview: {str(file_content)[:100]}...")
        else:
            st.markdown(f"Content: {file_content}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear file button
        if st.button("🗑️ File Remove Karein", use_container_width=True):
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
            st.rerun()
    
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
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
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
    
    # Clear Chat button with red styling
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History", use_container_width=True, key="clear_chat"):
        st.session_state.messages = []
        st.success("Chat history cleared successfully!")
        st.rerun()
    
    st.markdown("---")
    
    # quick prompts
    st.markdown("### 💡 Quick Prompts")
    quick_prompts = [
        "Explain quantum computing simply",
        "Write a Python function for Fibonacci",
        "Suggest healthy breakfast ideas",
        "Plan a 3-day trip to Karachi"
    ]
    
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state.quick_prompt = prompt
            st.rerun()
    
    # File related quick prompts
    if st.session_state.uploaded_file_content:
        st.markdown("### 📄 File Related Questions")
        file_prompts = [
            "Is file ka summary do",
            "File mein kya kya topics hain?",
            "File ki main points batao",
            "Is file se related kuch questions banao"
        ]
        
        for prompt in file_prompts:
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
    # File status display
    if st.session_state.uploaded_file_name:
        st.markdown(f'<div class="file-info-card">📁 Currently Active File: {st.session_state.uploaded_file_name}</div>', unsafe_allow_html=True)
    
    # chat container
    st.markdown("### 💬 Conversation")
    
    # Clear chat confirmation message
    if len(st.session_state.messages) == 0:
        st.info("💬 You can Choose also Prompt Chat.")
    
    # handle quick prompt
    if "quick_prompt" in st.session_state:
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
    else:
        prompt = st.chat_input("Please Type Your Message Here...", key="chat_input")
    
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
        # Agar file attached hai toh uske content ko context mein include karein
        if st.session_state.uploaded_file_content:
            file_context = f"\n\n[Attached File: {st.session_state.uploaded_file_name}]\nFile Content: {st.session_state.uploaded_file_content[:2000]}..." if len(str(st.session_state.uploaded_file_content)) > 2000 else f"\n\n[Attached File: {st.session_state.uploaded_file_name}]\nFile Content: {st.session_state.uploaded_file_content}"
            enhanced_prompt = f"{prompt}\n{file_context}"
        else:
            enhanced_prompt = prompt
        
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
                        for m in st.session_state.messages[:-1]  # Last message exclude karein kyunki woh enhanced hai
                    ] + [{"role": "user", "content": enhanced_prompt}],
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
                st.error("❌ Please Connect with API")
        
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
        {"icon": "💬", "title": "Multi-Topic", "desc": "Any subject expertise"},
        {"icon": "📁", "title": "File Support", "desc": "PDF, TXT, DOCX, CSV"},
        {"icon": "🗑️", "title": "Clear Chat", "desc": "One-click chat cleanup"}
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
    
    # file info card
    if st.session_state.uploaded_file_name:
        st.markdown("### 📄 Active File")
        st.markdown(f'<div class="stats-card">', unsafe_allow_html=True)
        st.markdown(f"**{st.session_state.uploaded_file_name}**")
        file_size = len(str(st.session_state.uploaded_file_content))
        st.markdown(f"Size: {file_size} chars")
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

# File status in footer
if st.session_state.uploaded_file_name:
    st.markdown(f"**📁 Active File:** {st.session_state.uploaded_file_name}")

# Add signature in main footer as well
st.markdown('<div class="footer-signature">Prepared by: Dr Fawad Hussain Paul</div>', unsafe_allow_html=True)


