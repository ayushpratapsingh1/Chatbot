import streamlit as st
import google.generativeai as genai
from typing import Iterator
import json
from datetime import datetime
import hashlib

# Configure page settings
st.set_page_config(page_title="🤖 Generative Model", page_icon="🤖", layout="wide")

# Add CSS for custom styling
st.markdown("""
<style>
    /* Modern dark theme */
    :root {
        --dark-bg: #343541;
        --darker-bg: #202123;
        --chat-bg: #444654;
        --text: #ECECF1;
        --input-bg: #40414F;
        --border: rgba(255,255,255,0.1);
        --orange: #FF4700;
    }

    /* Global styles */
    .stApp, .main .block-container {
        background: var(--dark-bg) !important;
        color: var(--text) !important;
        max-width: none !important;
        padding: 0 !important;
    }

    /* Sidebar */
    .css-1544g2n {
        background: var(--darker-bg) !important;
    }

    /* Chat layout */
    .chat-layout {
        display: flex;
        height: calc(100vh - 2rem);
        margin-top: -4rem;
    }

    /* Chat container */
    .chat-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        height: 100%;
        overflow: hidden;
    }

    /* Messages area */
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 2rem 0;
    }

    /* Message styling */
    .message-row {
        display: flex;
        padding: 1.5rem;
        border-bottom: 1px solid var(--border);
    }

    .message-row.user {
        background: var(--dark-bg);
    }

    .message-row.assistant {
        background: var(--chat-bg);
    }

    .message-content {
        max-width: 800px;
        margin: 0 auto;
        width: 100%;
        display: flex;
        gap: 1.5rem;
        align-items: flex-start;
        color: var(--text);
    }

    /* Avatar */
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .user .avatar {
        background: #5E5E5E;
    }

    .assistant .avatar {
        background: var(--orange);
    }

    /* Input container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 15.5rem;
        right: 0;
        padding: 1.5rem;
        background: var(--dark-bg);
        border-top: 1px solid var(--border);
    }

    .input-wrapper {
        max-width: 800px;
        margin: 0 auto;
        position: relative;
    }

    /* Chat input */
    .stChatInput {
        background: var(--input-bg) !important;
        border-color: var(--border) !important;
        padding: 1rem !important;
        color: var(--text) !important;
        border-radius: 0.75rem !important;
    }

    /* New chat button */
    .new-chat-btn {
        width: 100%;
        padding: 0.75rem;
        background: var(--orange);
        color: white;
        border: none;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .new-chat-btn:hover {
        opacity: 0.9;
    }

    /* History items */
    .history-item {
        padding: 0.75rem;
        border-radius: 0.5rem;
        color: var(--text);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        margin-bottom: 0.25rem;
        transition: background 0.2s;
    }

    .history-item:hover {
        background: rgba(255,255,255,0.1);
    }

    .history-item.active {
        background: rgba(255,71,0,0.2);
    }

    /* Welcome screen */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: var(--text);
        text-align: center;
        padding: 2rem;
    }

    .welcome-title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    .welcome-text {
        font-size: 1.1rem;
        opacity: 0.8;
    }

    /* Hide default elements */
    .stDeployButton, footer, header {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "api_key_configured" not in st.session_state:
    st.session_state.api_key_configured = False
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = {}

def create_chat_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_api_key_hash(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()[:8]

def get_safe_response(text):
    """Clean and escape response text"""
    if not text:
        return "I apologize, but I cannot generate that type of content."
    return text.replace("<", "&lt;").replace(">", "&gt;")

# Main container for flexible layout
main_container = st.container()

# API Key Input (shown prominently only if not configured)
if not st.session_state.api_key_configured:
    with main_container:
        st.title("🤖 Generative Model")
        google_api_key = st.text_input("Enter your Google API Key", type="password")
        if google_api_key:
            try:
                genai.configure(api_key=google_api_key)
                st.session_state.api_key = google_api_key
                st.session_state.api_key_configured = True
                st.session_state.api_key_hash = get_api_key_hash(google_api_key)
                st.rerun()
            except Exception as e:
                st.error("Invalid API Key")

# Main chat interface when API key is configured
if st.session_state.api_key_configured:
    # Sidebar with simplified chat history
    with st.sidebar:
        st.markdown("""
            <button class="new-chat-btn">
                <span>+ New chat</span>
            </button>
        """, unsafe_allow_html=True)
        
        # API key settings in compact form
        with st.expander("🔑 API Key", expanded=False):
            new_api_key = st.text_input("Update API Key", value="", type="password")
            if new_api_key:
                st.session_state.api_key = new_api_key
                st.session_state.api_key_hash = get_api_key_hash(new_api_key)
                st.rerun()
            st.caption(f"Current: ...{st.session_state.api_key_hash}")

        # New chat button at top
        if st.button("🆕 New Chat", use_container_width=True, type="primary"):
            st.session_state.current_chat_id = create_chat_id()
            st.session_state.messages = []
            st.rerun()

        # Simplified chat history
        st.markdown("### Chat History")
        
        for chat_id in sorted(st.session_state.chat_histories.keys(), reverse=True):
            chat_data = st.session_state.chat_histories[chat_id]
            is_active = chat_id == st.session_state.current_chat_id
            
            cols = st.columns([11, 1])
            with cols[0]:
                st.markdown(
                    f"""<div class="history-item {'active' if is_active else ''}" 
                        onclick="document.querySelector('[key=chat_{chat_id}]').click()">
                        💬 {chat_data.get('title', 'Untitled')}
                    </div>""",
                    unsafe_allow_html=True
                )
                st.button("", key=f"chat_{chat_id}", help="Load chat", type="secondary")
            
            with cols[1]:
                st.markdown(
                    f"""<div class="delete-btn" onclick="document.querySelector('[key=del_{chat_id}]').click()">
                        ×
                    </div>""",
                    unsafe_allow_html=True
                )
                st.button("", key=f"del_{chat_id}", help="Delete chat")

    # Main chat area with improved styling
    with main_container:
        st.markdown('<div class="chat-layout">', unsafe_allow_html=True)
        
        # Main chat area
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Messages area
        st.markdown('<div class="messages-container">', unsafe_allow_html=True)
        if not st.session_state.messages:
            show_welcome_screen()
        else:
            for message in st.session_state.messages:
                if message["role"] != "system":
                    display_message(message["role"], message["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area
        st.markdown(
            '<div class="input-container"><div class="input-wrapper">',
            unsafe_allow_html=True
        )
        # ...existing chat input code...
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

        try:
            # Configure Gemini with fixed settings
            model = genai.GenerativeModel(
                'gemini-pro',
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )

            # Initialize chat if needed
            if "messages" not in st.session_state:
                st.session_state.messages = []
                st.session_state.current_chat_id = create_chat_id()
                # Set Ayush personality
                system_msg = {"role": "system", "content": "You are Ayush, a helpful and friendly AI assistant. You are knowledgeable and aim to provide accurate, helpful responses while maintaining a conversational tone."}
                st.session_state.messages.append(system_msg)

            # Enhanced message display
            def display_message(role: str, content: str):
                """Display a message with consistent styling"""
                is_user = role == "user"
                st.markdown(f"""
                    <div class="message-row {role}">
                        <div class="message-content">
                            <div class="avatar">
                                {"👤" if is_user else "🤖"}
                            </div>
                            <div class="text">{content}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
            message_container = st.container()
            with message_container:
                for message in st.session_state.messages:
                    if message["role"] != "system":
                        display_message(message["role"], message["content"])
            st.markdown('</div>', unsafe_allow_html=True)

            # Improved chat input and response handling
            if prompt := st.chat_input("Message Ayush...", key="chat_input"):
                # Update chat history
                current_chat = {
                    'title': prompt[:40] + "..." if len(prompt) > 40 else prompt,
                    'messages': st.session_state.messages + [{"role": "user", "content": prompt}],
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.chat_histories[st.session_state.current_chat_id] = current_chat

                # Display user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                display_message("user", prompt)

                # Generate and display assistant response
                with st.spinner(""):
                    try:
                        chat = model.start_chat(history=[])
                        response = chat.send_message(prompt, stream=True)
                        response_text = ""
                        
                        placeholder = st.empty()
                        for chunk in response:
                            if (chunk.text):
                                response_text += get_safe_response(chunk.text)
                                placeholder.markdown(f"""
                                    <div class="chat-row assistant-row">
                                        <div class="chat-bubble">
                                            <div class="avatar">🤖</div>
                                            <div class="content">{response_text}▌</div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        if not response_text:
                            response_text = "I apologize, but I cannot generate that type of content."
                        
                        # Final response
                        placeholder.markdown(f"""
                            <div class="chat-row assistant-row">
                                <div class="chat-bubble">
                                    <div class="avatar">🤖</div>
                                    <div class="content">{response_text}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        current_chat['messages'] = st.session_state.messages
                        st.session_state.chat_histories[st.session_state.current_chat_id] = current_chat
                        
                    except Exception as e:
                        error_msg = "I apologize, but I encountered an error processing your request."
                        st.error(f"Error: {str(e)}")
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        except Exception as e:
            st.error(f"Error: {str(e)}")

else:
    st.info("Please enter your Google API key to start chatting.", icon="🔑")

# Simplified footer
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Powered by Ayush AI"
    "</div>", 
    unsafe_allow_html=True)

# Update the welcome screen
def show_welcome_screen():
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">AI-powered Chat System</h1>
            <p class="welcome-text">Start a conversation to begin your AI-powered learning journey</p>
            <div style="font-size: 4rem; margin-top: 2rem;">🤖</div>
        </div>
    """, unsafe_allow_html=True)
