"""
Welcome component for the Groww Mutual Fund Chatbot
Displays title, example questions, and available schemes
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


def render_schemes_section():
    """
    Render the available schemes section (for left quadrant)
    """
    # Available schemes section
    st.markdown(
        """
        <div style='margin: 0 0 15px 0;'>
            <h3 style='color: #1F2937; margin-bottom: 8px; font-size: 1.1rem; font-weight: 600;'>
                <span style='font-size: 16px;'>📋</span> Available Schemes
            </h3>
            <p style='color: #6B7280; margin-bottom: 12px; font-size: 12px; line-height: 1.4;'>
                I can answer questions about the following SBI Mutual Fund schemes:
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display schemes as compact square boxes
    cols = st.columns(2)
    for idx, scheme in enumerate(AVAILABLE_SCHEMES):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style='background: #FFFFFF; 
                            border: 2px solid #10B981; border-radius: 8px; padding: 8px 10px; 
                            margin-bottom: 8px; text-align: center; transition: all 0.3s;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.08); min-height: 50px; display: flex; align-items: center; justify-content: center;'>
                    <p style='color: #10B981; font-weight: 600; font-size: 11px; margin: 0; line-height: 1.3;'>{scheme}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_example_questions():
    """
    Render the example questions section (for left quadrant)
    """
    # Example questions section
    st.markdown(
        """
        <div style='margin: 20px 0 12px 0;'>
            <h3 style='color: #1F2937; margin-bottom: 8px; font-size: 1.1rem; font-weight: 600;'>
                <span style='font-size: 16px;'>💡</span> Sample Queries
            </h3>
            <p style='color: #6B7280; margin-bottom: 12px; font-size: 12px; line-height: 1.4;'>
                Click on any example question below to get started:
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display example question chips - compact square boxes in 2 columns
    cols = st.columns(2)
    for idx, question in enumerate(EXAMPLE_QUESTIONS):
        with cols[idx % 2]:
            # Create a styled button that looks like a compact square box
            button_style = """
                <style>
                    div[data-testid="stButton"] > button[kind="secondary"] {
                        background: #FFFFFF;
                        color: #10B981;
                        border: 2px solid #10B981;
                        border-radius: 8px;
                        padding: 8px 10px;
                        font-weight: 500;
                        font-size: 11px;
                        transition: all 0.3s ease;
                        width: 100%;
                        text-align: center;
                        white-space: normal;
                        height: auto;
                        min-height: 50px;
                        margin-bottom: 8px;
                        line-height: 1.3;
                    }
                    div[data-testid="stButton"] > button[kind="secondary"]:hover {
                        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                        color: #FFFFFF;
                        border-color: #10B981;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                    }
                </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
        
        if st.button(
            question,
            key=f"example_{idx}",
            use_container_width=True,
            type="secondary"
        ):
            # Store the question in session state to populate input
            st.session_state.example_question = question
            st.rerun()


def render_header():
    """
    Legacy function - title is now rendered in app.py
    Kept for backward compatibility
    """
    pass

def render_welcome():
    """
    Legacy function - kept for backward compatibility
    Renders schemes and example questions
    """
    render_schemes_section()
    render_example_questions()


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

