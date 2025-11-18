"""
Welcome component for the SBI Mutual Fund FAQ Chatbot
Displays welcome message, logos, example questions, and available schemes
"""

import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.query_processor import AVAILABLE_SCHEMES

# Example questions
EXAMPLE_QUESTIONS = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?"
]


def render_welcome():
    """
    Render the welcome section with logos, message, example questions, and available schemes
    """
    # Create columns for logos
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Groww logo
        groww_logo_path = "frontend/assets/logos/groww_logo.png"
        if os.path.exists(groww_logo_path):
            st.image(groww_logo_path, width=120)
        else:
            # Placeholder if logo not found
            st.markdown("**Groww**")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='color: #0F4C75; margin-bottom: 10px;'>SBI Mutual Fund FAQ Chatbot</h1>
                <p style='color: #1F2937; font-size: 18px;'>Your trusted partner for factual information</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        # SBI Mutual Fund logo
        sbi_logo_path = "frontend/assets/logos/sbi_mutual_fund_logo.png"
        if os.path.exists(sbi_logo_path):
            st.image(sbi_logo_path, width=150)
        else:
            # Placeholder if logo not found
            st.markdown("**SBI Mutual Fund**")
    
    # Welcome message section
    st.markdown("---")
    
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #0F4C75 0%, #0891B2 100%); 
                    color: white; padding: 30px; border-radius: 12px; margin: 20px 0;'>
            <h2 style='color: white; margin-bottom: 15px;'>Welcome! 👋</h2>
            <p style='color: rgba(255, 255, 255, 0.95); font-size: 16px; line-height: 1.6;'>
                I'm here to help you with factual information about SBI Mutual Fund schemes. 
                I can answer questions about expense ratios, exit loads, minimum investments, 
                lock-in periods, risk ratings, benchmarks, and more.
            </p>
            <p style='color: rgba(255, 255, 255, 0.9); font-size: 14px; margin-top: 15px;'>
                <strong>Note:</strong> I provide factual information only. For personalized investment 
                guidance, please consult a SEBI-registered advisor.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Available schemes section
    st.markdown("### 📋 Available Schemes")
    st.markdown(
        f"""
        <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; margin: 15px 0;'>
            <p style='color: #1F2937; margin-bottom: 10px;'>
                I can answer questions about the following SBI Mutual Fund schemes:
            </p>
            <ul style='color: #1F2937; line-height: 2;'>
        """,
        unsafe_allow_html=True
    )
    
    for scheme in AVAILABLE_SCHEMES:
        st.markdown(f"<li style='color: #0F4C75;'><strong>{scheme}</strong></li>", unsafe_allow_html=True)
    
    st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Example questions section
    st.markdown("### 💡 Try asking:")
    st.markdown(
        "<p style='color: #1F2937; margin-bottom: 15px;'>Click on any example question below to get started:</p>",
        unsafe_allow_html=True
    )
    
    # Display example question chips
    cols = st.columns(3)
    for idx, (col, question) in enumerate(zip(cols, EXAMPLE_QUESTIONS)):
        with col:
            # Create a button that looks like a chip
            if st.button(
                question,
                key=f"example_{idx}",
                use_container_width=True,
                type="secondary"
            ):
                # Store the question in session state to populate input
                st.session_state.example_question = question
                st.rerun()
    
    # Additional information
    st.markdown("---")
    st.markdown(
        """
        <div style='background-color: #E5E7EB; padding: 15px; border-radius: 8px; margin-top: 20px;'>
            <p style='color: #1F2937; font-size: 14px; margin: 0;'>
                <strong>💡 Tip:</strong> You can ask questions like:
            </p>
            <ul style='color: #1F2937; font-size: 13px; margin-top: 10px;'>
                <li>"What is the expense ratio of [Scheme Name]?"</li>
                <li>"What is the minimum SIP for [Scheme Name]?"</li>
                <li>"What is the exit load for [Scheme Name]?"</li>
                <li>"What is the lock-in period for [Scheme Name]?"</li>
                <li>"What is the riskometer rating of [Scheme Name]?"</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_example_question():
    """
    Get and clear the example question from session state
    
    Returns:
        Example question string or None
    """
    if 'example_question' in st.session_state:
        question = st.session_state.example_question
        # Clear it after retrieving
        del st.session_state.example_question
        return question
    return None

