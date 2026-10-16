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
        padding: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #004d99;
    }
    .local-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 10px 15px;
        border-radius: 8px;
        color: #856404;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    .app-version {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: bold;
        padding-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

try:
    groq_key = st.secrets["GROQ_API_KEY"]
    GEMINI_KEYS = [
        st.secrets["GEMINI_KEY_1"],
        st.secrets["GEMINI_KEY_2"],
        st.secrets["GEMINI_KEY_3"],
        st.secrets["GEMINI_KEY_4"]
    ]
except Exception as e:
    st.error("⚠️ تنبيه أمني: لم يتم العثور على المفاتيح السرية في إعدادات المنصة (Secrets). يرجى إضافتها ليعمل التطبيق بشكل صحيح.")
    st.stop()

groq_client = Groq(api_key=groq_key)

def analyze_image_with_fallback(image, prompt):
    last_error = None
    for key in GEMINI_KEYS:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            last_error = e
            continue
    raise Exception(f"نفدت الحصة لجميع مفاتيح Gemini المتاحة. الخطأ الأخير: {last_error}")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=55)
    st.title("META SCAN")
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    menu_option = st.radio(
        "القائمة الرئيسية:",
        [
            "الرئيسية", 
            "دليل معايير مجتمع Meta", 
            "سياسة الخصوصية", 
            "سياسة المستخدم", 
            "عن التطبيق", 
            "راسل التطبيق"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="app-version">نسخة v1.0</div>', unsafe_allow_html=True)

if menu_option == "الرئيسية":
    st.markdown("""
        <div class="main-header">
            <h1>🛡️ META SCAN</h1>
            <p>النظام الذكي المتكامل لفحص النصوص والإعلانات المرئية وتجنب الحظر</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### ✍️ فحص نصوص المنشور")
    post_content = st.text_area("نص المنشور:", height=120, placeholder="اكتب نص الإعلان أو المنشور هنا...", key="text_input_area")

    if st.button("🔍 ابدأ فحص النص العميق", key="btn_text_scan"):
        if not post_content.strip():
            st.warning("⚠️ الرجاء كتابة نص المنشور أولاً.")
        else:
            found_local_words = [w for words in SUSPICIOUS_KEYWORDS.values() for w in words if w in post_content]
            
            with st.spinner("⏳ جاري التحليل العميق للسياق بواسطة Llama 3.1..."):
                try:
                    system_prompt = "أنت خبير محترف في سياسات وإعلانات منصات Meta. قم بتحليل النص المدخل بدقة، وبين مدى مطابقته للمعايير وسياسات المجتمع، وحدد الكلمات الحساسة واقترح تعديلات بديلة مضمونة الأمان."
                    completion = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": post_content}],
                        temperature=0.3,
                        max_tokens=1024
                    )
                    
                    st.success("✅ تم فحص النص بنجاح!")
                    
                    if found_local_words:
                        st.markdown(f'<div class="local-warning"><b>⚠️ تنبيه من المساعد المحلي:</b> تم رصد كلمات/مصطلحات حساسة في النص: <code>{", ".join(found_local_words)}</code></div>', unsafe_allow_html=True)
                    
                    st.markdown("### 📊 تقرير تحليل النص:")
                    st.markdown(completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box
