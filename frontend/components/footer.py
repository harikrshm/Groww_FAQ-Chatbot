"""
Footer component with disclaimer and links to official pages
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SEBI_EDUCATION_LINK, AMFI_LINK, SBI_MF_LINK


def render_footer():
    """
    Render footer with disclaimer and links to SEBI/AMFI/SBI MF official pages
    """
    st.markdown("---")
    
    st.markdown(
        """
        <div style='background-color: #FFFFFF; padding: 25px 20px; margin-top: 30px; 
                    border-top: 2px solid #E5E7EB; text-align: center;'>
            <div style='max-width: 800px; margin: 0 auto;'>
                <h4 style='color: #1F2937; margin-bottom: 12px; font-size: 16px; font-weight: 600;'>Important Disclaimer</h4>
                <p style='color: #1F2937; font-size: 14px; line-height: 1.6; margin-bottom: 20px;'>
                    This chatbot provides factual information only about SBI Mutual Fund schemes. 
                    It does not provide investment advice, recommendations, or opinions. 
                    For personalized investment guidance, please consult a SEBI-registered investment advisor.
                </p>
            </div>
        </div>
        <style>
            a.footer-link {{
                background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
                color: #FFFFFF !important; 
                text-decoration: none; 
                font-weight: 600; 
                padding: 10px 20px; 
                border: 2px solid #8B5CF6; 
                border-radius: 8px; 
                transition: all 0.3s; 
                display: inline-block; 
                font-size: 14px;
                box-shadow: 0 2px 6px rgba(139, 92, 246, 0.25);
                margin: 5px;
            }}
            a.footer-link:hover {{
                background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
                text-decoration: none;
                color: #FFFFFF !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Render links separately to avoid large text box
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(
            f'<a href="{SEBI_EDUCATION_LINK}" target="_blank" class="footer-link"><span style="font-size: 12px;">📘</span> SEBI</a>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<a href="{AMFI_LINK}" target="_blank" class="footer-link"><span style="font-size: 12px;">📗</span> AMFI</a>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<a href="{SBI_MF_LINK}" target="_blank" class="footer-link"><span style="font-size: 12px;">🏦</span> SBI Mutual Fund</a>',
            unsafe_allow_html=True
        )
