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
        <div style='background-color: #F8F9FA; padding: 30px 20px; margin-top: 40px; 
                    border-top: 2px solid #E5E7EB; text-align: center;'>
            <div style='max-width: 800px; margin: 0 auto;'>
                <h4 style='color: #1F2937; margin-bottom: 15px;'>Important Disclaimer</h4>
                <p style='color: #1F2937; font-size: 14px; line-height: 1.6; margin-bottom: 20px;'>
                    This chatbot provides factual information only about SBI Mutual Fund schemes. 
                    It does not provide investment advice, recommendations, or opinions. 
                    For personalized investment guidance, please consult a SEBI-registered investment advisor.
                </p>
                
                <div style='display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin: 20px 0;'>
                    <a href='{}' target='_blank' 
                       style='color: #0891B2; text-decoration: none; font-weight: 600; 
                              padding: 8px 16px; border: 2px solid #0891B2; border-radius: 6px; 
                              transition: all 0.3s; display: inline-block;'>
                        📘 SEBI
                    </a>
                    <a href='{}' target='_blank' 
                       style='color: #0891B2; text-decoration: none; font-weight: 600; 
                              padding: 8px 16px; border: 2px solid #0891B2; border-radius: 6px; 
                              transition: all 0.3s; display: inline-block;'>
                        📗 AMFI
                    </a>
                    <a href='{}' target='_blank' 
                       style='color: #0891B2; text-decoration: none; font-weight: 600; 
                              padding: 8px 16px; border: 2px solid #0891B2; border-radius: 6px; 
                              transition: all 0.3s; display: inline-block;'>
                        🏦 SBI Mutual Fund
                    </a>
                </div>
                
                <p style='color: #6B7280; font-size: 12px; margin-top: 20px; line-height: 1.5;'>
                    Mutual fund investments are subject to market risks. Please read all scheme related documents carefully before investing.
                    <br>
                    Past performance is not indicative of future results.
                </p>
                
                <p style='color: #9CA3AF; font-size: 11px; margin-top: 15px;'>
                    © 2024 SBI Mutual Fund FAQ Chatbot | Powered by Groww
                </p>
            </div>
        </div>
        """.format(SEBI_EDUCATION_LINK, AMFI_LINK, SBI_MF_LINK),
        unsafe_allow_html=True
    )

