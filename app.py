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

st.set_page_config(page_title="META SCAN", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

# CSS مصمم خصيصاً لضغط الفراغات وضبط الألوان والتوافق مع الموبايل
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*='css'] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
}

/* تقليل الفراغات العلوية والسفلية بالصفحة */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}

.stTextInput, .stTextArea, .stSelectbox, .stMarkdown, h1, h2, h3, h4, h5, h6, p, div {
    direction: rtl;
    text-align: right;
}

/* إخفاء القائمة الجانبية تماماً لمنع التداخل */
[data-testid="stSidebar"] {
    display: none !important;
}

/* الهيدر الرئيسي المدمج والمضغوط */
.main-header {
    background: linear-gradient(135deg, #0068c4 0%, #002b5c 100%);
    padding: 12px 10px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 10px;
}
.main-header h
