"""
Chat UI components for the SBI Mutual Fund FAQ Chatbot
Includes message bubbles, input area, and send button
"""

import streamlit as st
from typing import List, Dict, Optional


def render_message_bubble(message: str, is_user: bool, source_url: Optional[str] = None):
    """
    Render a message bubble (user or bot)
    
    Args:
        message: Message text to display
        is_user: True if user message, False if bot message
        source_url: Optional source URL to display below bot messages
    """
    if is_user:
        # User message - right aligned, blue background
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-end; margin: 12px 0;'>
                <div style='background-color: #0F4C75; color: white; padding: 12px 16px; 
                            border-radius: 12px; max-width: 70%; word-wrap: break-word; 
                            border-bottom-right-radius: 4px;'>
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Bot message - left aligned, gray background
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-start; margin: 12px 0;'>
                <div style='background-color: #E5E7EB; color: #1F2937; padding: 12px 16px; 
                            border-radius: 12px; max-width: 70%; word-wrap: break-word; 
                            border-bottom-left-radius: 4px;'>
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display source URL badge if available
        if source_url:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start; margin-top: -8px; margin-bottom: 12px;'>
                    <a href='{source_url}' target='_blank' 
                       style='background-color: #10B981; color: white; padding: 4px 12px; 
                              border-radius: 12px; font-size: 12px; text-decoration: none; 
                              display: inline-block;'>
                        📎 View Source
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_chat_history(chat_history: List[Dict]):
    """
    Render the chat history
    
    Args:
        chat_history: List of message dictionaries with 'role', 'content', and optionally 'source_url'
    """
    if not chat_history:
        return
    
    # Create a container for chat messages
    st.markdown(
        """
        <div style='background-color: white; border-radius: 12px; padding: 20px; 
                    margin: 20px 0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); 
                    min-height: 400px; max-height: 600px; overflow-y: auto;'>
        """,
        unsafe_allow_html=True
    )
    
    # Render each message
    for msg in chat_history:
        role = msg.get('role', 'bot')
        content = msg.get('content', '')
        source_url = msg.get('source_url', None)
        
        is_user = (role == 'user')
        render_message_bubble(content, is_user, source_url if not is_user else None)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_input_area():
    """
    Render the input area with text input and send button
    
    Returns:
        Tuple of (user_input, send_clicked)
        - user_input: The text entered by the user
        - send_clicked: True if send button was clicked
    """
    # Create columns for input and button
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your question here...",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Ask about expense ratios, exit loads, minimum SIP, etc..."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Align button with input
        send_clicked = st.button("Send", type="primary", use_container_width=True)
    
    return user_input, send_clicked


def render_loading_indicator():
    """
    Render a loading indicator for when the bot is processing
    """
    st.markdown(
        """
        <div style='display: flex; justify-content: flex-start; margin: 12px 0;'>
            <div style='background-color: #E5E7EB; color: #1F2937; padding: 12px 16px; 
                        border-radius: 12px; border-bottom-left-radius: 4px;'>
                <div style='display: flex; align-items: center;'>
                    <div style='border: 3px solid #E5E7EB; border-top: 3px solid #0F4C75; 
                                border-radius: 50%; width: 20px; height: 20px; 
                                animation: spin 1s linear infinite; margin-right: 10px;'></div>
                    <span>Thinking...</span>
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

