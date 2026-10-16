# ------------------------------------------------------------------
# META SCAN Application
# Copyright (c) 2026 Sakhr AlHubaish. All Rights Reserved.
# Proprietary and Confidential - Developed for Meta Compliance Scanning
# ------------------------------------------------------------------

import streamlit as st
import os
from groq import Groq
import google.generativeai as genai
from PIL import Image
from local_filter import SUSPICIOUS_KEYWORDS

st.set_page_config(
    page_title="META SCAN",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنسيق CSS متجاوب كلياً ومخصص لتحويل أزرار القائمة إلى خطوط نحيفة وأنيقة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stTextInput, .stTextArea, .stSelectbox {
        direction: rtl;
    }
    
    div.row-widget.stRadio > div {
        background-color: transparent;
        gap: 5px;
    }
    div.row-widget.stRadio label {
        background-color: #1e293b;
        color: #ffffff !important;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        width: 100%;
        display: block;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    div.row-widget.stRadio label:hover {
        background-color: #0068c4;
        border-color: #0068c4;
    }

    .main-header {
        background: linear-gradient(135deg, #0068c4 0%, #002b5c 100%);
        padding: 20px 15px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        word-wrap: break-word;
    }
    .main-header h1 {
        font-size: 1.8rem;
        margin-bottom: 8px;
    }
    .main-header p {
        font-size: 0.9rem;
        margin: 0;
    }
    .section-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    .custom-divider {
        border: none;
        height: 1px;
        background-color: rgba(255, 255, 255, 0.3);
        margin: 12px 0;
    }
    .custom-divider-dark {
        border: none;
        height: 1px;
        background-color: #dee2e6;
        margin: 15px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #0068c4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10
