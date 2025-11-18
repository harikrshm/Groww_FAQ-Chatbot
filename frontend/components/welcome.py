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

# Example question with pre-computed answer
EXAMPLE_QUESTION = "What is the minimum SIP for SBI Small Cap Fund?"
EXAMPLE_QUESTIONS = [EXAMPLE_QUESTION]  # Keep as list for backward compatibility

# Pre-computed answer for the example question
EXAMPLE_QUESTION_ANSWER = {
    'query': "What is the minimum SIP for SBI Small Cap Fund?",
    'answer': "The minimum SIP amount for SBI Small Cap Fund is ₹ 500. Last updated from sources.",
    'source_url': "https://www.sbimf.com"
}


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
    Render the example question section (for left quadrant) - redesigned for single question
    """
    # Example question section
    st.markdown(
        """
        <div style='margin: 20px 0 12px 0;'>
            <h3 style='color: #1F2937; margin-bottom: 8px; font-size: 1.1rem; font-weight: 600;'>
                <span style='font-size: 16px;'>💡</span> Sample Query
            </h3>
            <p style='color: #6B7280; margin-bottom: 12px; font-size: 12px; line-height: 1.4;'>
                Click on the example question below to see a sample answer:
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display single example question - full width, styled button
    button_style = """
        <style>
            div[data-testid="stButton"] > button[kind="secondary"] {
                background: #FFFFFF !important;
                color: #10B981 !important;
                border: 2px solid #10B981 !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
                font-weight: 500 !important;
                font-size: 12px !important;
                transition: all 0.3s ease !important;
                width: 100% !important;
                text-align: center !important;
                white-space: normal !important;
                height: auto !important;
                min-height: 60px !important;
                margin-bottom: 12px !important;
                line-height: 1.4 !important;
            }
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
                color: #FFFFFF !important;
                border-color: #10B981 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
            }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    # Display the example question button
    if st.button(
        EXAMPLE_QUESTION,
        key="example_question_btn",
        use_container_width=True,
        type="secondary"
    ):
        # Store the question and answer in session state
        st.session_state.example_question = EXAMPLE_QUESTION
        st.session_state.example_question_answer = EXAMPLE_QUESTION_ANSWER
        st.rerun()
    
    # Display pre-computed answer if example question was clicked
    if 'example_question_answer' in st.session_state:
        answer_data = st.session_state.example_question_answer
        st.markdown(
            f"""
            <div style='background: #F0FDF4; border: 2px solid #10B981; border-radius: 8px; 
                        padding: 12px; margin-top: 12px;'>
                <p style='color: #1F2937; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>
                    Sample Answer:
                </p>
                <p style='color: #374151; font-size: 11px; line-height: 1.5; margin-bottom: 8px;'>
                    {answer_data['answer']}
                </p>
                <a href='{answer_data['source_url']}' target='_blank' 
                   style='color: #10B981; font-size: 10px; text-decoration: none; font-weight: 500;'>
                    📎 View Source
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )


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

