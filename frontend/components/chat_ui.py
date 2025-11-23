"""
Chat UI components for the SBI Mutual Fund FAQ Chatbot
Includes message bubbles, input area, and send button
"""

import streamlit as st
from typing import List, Dict, Optional


def render_message_bubble(message: str, is_user: bool, source_url: Optional[str] = None):
    """
    Render a message bubble (user or bot) with modern styling inspired by shadcn-chatbot-kit
    
    Args:
        message: Message text to display
        is_user: True if user message, False if bot message
        source_url: Optional source URL to display below bot messages
    """
    if is_user:
        # User message - right aligned, green gradient background
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-end; margin: 8px 0; padding: 0 4px;'>
                <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                            color: #FFFFFF; padding: 12px 16px; border-radius: 16px; 
                            max-width: 75%; word-wrap: break-word; border-bottom-right-radius: 4px;
                            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
                            line-height: 1.5; font-size: 14px;'>
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Bot message - left aligned, white background with green border
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-start; margin: 8px 0; padding: 0 4px;'>
                <div style='background-color: #FFFFFF; color: #1F2937; padding: 12px 16px; 
                            border-radius: 16px; max-width: 75%; word-wrap: break-word; 
                            border-bottom-left-radius: 4px; border: 2px solid #10B981;
                            box-shadow: 0 1px 4px rgba(16, 185, 129, 0.15);
                            line-height: 1.6; font-size: 14px;'>
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display source URL badge if available - using purple accent color
        # Check for both None and empty string
        if source_url and source_url.strip():
            # Escape HTML in URL to prevent XSS
            import html
            escaped_url = html.escape(source_url.strip())
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start; margin-top: 4px; 
                            margin-bottom: 8px; padding: 0 4px;'>
                    <a href='{escaped_url}' target='_blank' rel='noopener noreferrer'
                       style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
                              color: #FFFFFF; padding: 6px 12px; border-radius: 12px; 
                              font-size: 11px; font-weight: 600; text-decoration: none; 
                              display: inline-flex; align-items: center; gap: 4px;
                              box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3);
                              transition: all 0.3s ease;'>
                        <span style='font-size: 11px;'>📎</span>
                        <span>View Source</span>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_chat_history(chat_history: List[Dict]):
    """
    Render the chat history with modern container styling
    
    Args:
        chat_history: List of message dictionaries with 'role', 'content', and optionally 'source_url'
    """
    if not chat_history:
        return
    
    # Create a modern container for chat messages with proper scrolling
    # Removed min-height to prevent empty white space
    st.markdown(
        """
        <div id="chat-container" style='background-color: #FFFFFF; border-radius: 16px; 
                    padding: 16px; margin: 0 0 12px 0; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); 
                    max-height: 60vh; overflow-y: auto;
                    border: 2px solid #E5E7EB;'>
        """,
        unsafe_allow_html=True
    )
    
    # Render each message
    for msg in chat_history:
        role = msg.get('role', 'bot')
        content = msg.get('content', '')
        source_url = msg.get('source_url', None)
        
        # Ensure source_url is not empty string
        if source_url and isinstance(source_url, str) and not source_url.strip():
            source_url = None
        
        is_user = (role == 'user')
        render_message_bubble(content, is_user, source_url if not is_user else None)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Auto-scroll to bottom script with smooth scrolling
    st.markdown(
        """
        <script>
            // Auto-scroll chat container to bottom with smooth animation
            setTimeout(function() {
                var container = document.getElementById('chat-container');
                if (container) {
                    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
                }
            }, 100);
        </script>
        """,
        unsafe_allow_html=True
    )


def render_input_area():
    """
    Render the input area with text input and send button (positioned in right column)
    
    Returns:
        Tuple of (user_input, send_clicked)
        - user_input: The text entered by the user
        - send_clicked: True if send button was clicked
    """
    # Add custom styling for input area with green color palette
    st.markdown(
        """
        <style>
            .stTextInput > div > div > input {
                border: 2px solid #E5E7EB;
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 14px;
                background-color: #FFFFFF;
                transition: all 0.3s ease;
                color: #1F2937;
            }
            .stTextInput > div > div > input:focus {
                border-color: #10B981;
                outline: none;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            .stTextInput > div > div > input::placeholder {
                color: #9CA3AF;
            }
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: #FFFFFF;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 6px rgba(16, 185, 129, 0.25);
            }
            .stButton > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
            }
            .stButton > button[kind="primary"]:active {
                transform: translateY(0);
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create columns for input and button - compact design
    col1, col2 = st.columns([4.5, 1], gap="small")
    
    with col1:
        user_input = st.text_input(
            "Type your question here...",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Ask about expense ratios, exit loads, minimum SIP, etc..."
        )
    
    with col2:
        send_clicked = st.button("Send", type="primary", use_container_width=True)
    
    return user_input, send_clicked


def render_loading_indicator():
    """
    Render a modern loading indicator for when the bot is processing
    """
    st.markdown(
        """
        <div style='display: flex; justify-content: flex-start; margin: 8px 0; padding: 0 4px;'>
            <div style='background-color: #FFFFFF; color: #1F2937; padding: 12px 16px; 
                        border-radius: 16px; border-bottom-left-radius: 4px; 
                        border: 2px solid #10B981; box-shadow: 0 1px 4px rgba(16, 185, 129, 0.15);'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <div style='border: 3px solid #E5E7EB; border-top: 3px solid #10B981; 
                                border-radius: 50%; width: 20px; height: 20px; 
                                animation: spin 1s linear infinite;'></div>
                    <span style='font-size: 14px; color: #6B7280;'>Thinking...</span>
                </div>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def add_message_to_history(role: str, content: str, source_url: Optional[str] = None):
    """
    Add a message to the chat history in session state
    
    Args:
        role: 'user' or 'bot'
        content: Message content
        source_url: Optional source URL for bot messages
    """
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Normalize source_url - convert empty strings to None
    if source_url and isinstance(source_url, str):
        source_url = source_url.strip() if source_url.strip() else None
    elif not source_url:
        source_url = None
    
    message = {
        'role': role,
        'content': content,
        'source_url': source_url
    }
    
    st.session_state.chat_history.append(message)


def clear_chat_history():
    """Clear the chat history"""
    if 'chat_history' in st.session_state:
        st.session_state.chat_history = []


def get_chat_history() -> List[Dict]:
    """
    Get the current chat history
    
    Returns:
        List of message dictionaries
    """
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    return st.session_state.chat_history

