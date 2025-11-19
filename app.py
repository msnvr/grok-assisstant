# app.py - Streamlit MVP (converted from our PySide6 beast)
import streamlit as st
import openai
import os
import json
import time
import base64
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Config
openai.api_key = os.getenv()
if not openai.api_key:
    st.error("⚠️ Please set your OPENAI_API_KEY in a .env file or Streamlit secrets!")
    st.stop()

# App config
st.set_page_config(
    page_title="Grok-Inspired Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it feel premium (very close to the PySide6 dark elegance)
st.markdown("""
<style>
    .main { background-color: #0e0e0e; color: #e0e0e0; }
    .stChatMessage { margin-bottom: 1.5rem; }
    .user-message { background-color: #1e1e1e; border-radius: 12px; padding: 12px; }
    .assistant-message { background-color: #2d2d2d; border-radius: 12px; padding: 12px; border-left: 4px solid #00ff99; }
    .stTextInput > div > div > input { background-color: #1e1e1e; color: white; border-radius: 12px; }
    .sidebar .sidebar-content { background-color: #111111; }
    .model-badge { background: linear-gradient(90deg, #00ff99, #00b8ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🤖 Grok-Inspired Assistant")
    st.markdown("---")
    
    model = st.selectbox(
        "Model",
        ["grok-beta", "gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
        index=0
    )
    
    temperature = st.slider("Temperature", 0.0, 2.0, 0.9, 0.1)
    max_tokens = st.slider("Max Tokens", 100, 8192, 2048, 100)
    
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.success("Conversation cleared!")
    
    st.caption(f"Streamlit MVP • {datetime.now().strftime('%Y-%m-%d')}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! I'm your Grok-inspired assistant — maximally truth-seeking, slightly rebellious, and ready to go deep. What’s on your mind today? 🚀"
        }
    ]

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message(msg["role"], avatar="🧑‍💻"):
            st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        with st.chat_message(msg["role"], avatar="🤖"):
            st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)

    # Assistant response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        # Streaming response
        try:
            stream = openai.chat.completions.create(
                model=model if model.startswith("gpt") else "grok-beta",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(f"<div class='assistant-message'>{full_response}▌</div>", unsafe_allow_html=True)
            
            message_placeholder.markdown(f"<div class='assistant-message'>{full_response}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"OpenAI error: {e}")

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit • Inspired by Grok & xAI")
