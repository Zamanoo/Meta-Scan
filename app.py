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
    initial_sidebar_state="collapsed"  # مغلقة افتراضياً في الجوال لمنع التداخل
)

# تنسيق CSS محسن ومتجاوب كلياً للهواتف المحمولة لمنع تداخل الحروف والعناصر
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
        font-size: 0.95rem;
        margin: 0;
    }
    .section-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    /* فواصل بيضاء ونحيفة ونظيفة */
    .custom-divider {
        border: none;
        height: 1px;
        background-color: rgba(255, 255, 255, 0.4);
        margin: 15px 0;
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
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: bold;
        padding-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# سحب المفاتيح بأمان من إعدادات المنصة (st.secrets)
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

# ==========================================
# القائمة الجانبية (Sidebar Navigation)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=60)
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
        index=0
    )
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="app-version">نسخة v1.0</div>', unsafe_allow_html=True)

# ==========================================
# عرض المحتوى حسب اختيار المستخدم
# ==========================================

if menu_option == "الرئيسية":
    st.markdown("""
        <div class="main-header">
            <h1>🛡️ META SCAN</h1>
            <p>النظام الذكي المتكامل لفحص النصوص والإعلانات المرئية وتجنب الحظر</p>
        </div>
    """, unsafe_allow_html=True)

    # فحص النصوص
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

    # فحص الصور
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### 🖼️ فحص صور المنشور")
    uploaded_image = st.file_uploader("اختر ملف الصورة (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"], key="image_upload_area")

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة للفحص", use_column_width=True)
        if st.button("🔍 ابدأ فحص الصورة الذكي", key="btn_image_scan"):
            with st.spinner("⏳ جاري تحليل الصورة والعناصر البصرية عبر Gemini..."):
                try:
                    prompt = "قم بتحليل هذه الصورة لإعلان تجاري لـ Meta. وضح هل تخالف السياسات (نصوص كثيرة، وعود مضللة، صور حساسة أو سياسية) وما هي التعديلات المطلوبة على التصميم لضمان قبوله."
                    res_text = analyze_image_with_fallback(image, prompt)
                    st.success("✅ تم تحليل الصورة بنجاح!")
                    st.markdown("### 📊 تقرير تحليل الصورة:")
                    st.markdown(res_text)
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء فحص الصورة: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "دليل معايير مجتمع Meta":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### 📖 دليل معايير مجتمع Meta")
    st.write("يعتمد فاحص **META SCAN** على تحليل المحتوى وفقاً لأبرز بنود السياسة والمعايير المعتمدة التالية من Meta:")
    st.markdown("""
    1. **العنف والتحريض (Violence & Incitement):** منع الترويج للأعمال العنفية، التهديدات، أو الأسلحة.
    2. **خطاب الكراهية (Hate Speech):** محاربة الهجوم على الأفراد أو المجموعات بناءً على العرق، الدين، الجنس، أو الانتماء.
    3. **المحتوى الجنسي والعري (Sexually Explicit):** منع الترويج للصور أو العبارات الفاضحة والمحتوى البالغ غير المرخص.
    4. **الخطاب المضلل والمعلومات الكاذبة (Misinformation):** تجنب الأخبار المزيفة أو المضللة المؤثرة على السلامة العامة والانتخابات.
    5. **الملكية الفكرية وحقوق النشر (Intellectual Property):** حماية حقوق الملكية والقرصنة والعلامات التجارية.
    6. **المنتجات والخدمات المقيدة:** كالسلع المقيدة والعمليات المالية والعملات غير المرخصة.
    7. **الأمان والخصوصية:** منع مشاركة المعلومات الشخصية للآخرين (Doxxing).
    8. **التنمر والتحرش:** منع الإساءة المباشرة والمضايقات الرقمية.
    9. **الاحتيال والخداع:** منع الترويج للأنشطة المالية المشبوهة أو الوهمية.
    10. **السلع والخدمات الخاضعة للرقابة:** الأدوية غير المرخصة والمواد المخدرة.
    11. **الانتحار أو إيذاء النفس:** منع تشجيع أو وصف وسائل إيذاء النفس.
    12. **التطرف العنيف والإرهاب:** حظر المنظمات الإرهابية والترويج لأفكارها.
    13. **التلاعب بالنظام والبريد العشوائي (Spam):** نشر الروابط الوهمية والتفاعل الزائف.
    14. **الأخبار الزائفة والصحية:** تضليل الجمهور بشأن القضايا الصحية والطبية.
    15. **الاحتيال التجاري والاعلانات المضللة:** ضمان مصداقية العروض التجارية والإعلانات الممولة.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة الخصوصية":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### 🔒 سياسة الخصوصية")
    st.write("نحن نحترم خصوصيتك ونلتزم بحماية بياناتك الشخصية. إليك تفاصيل التعامل مع البيانات في تطبيق **META SCAN**:")
    st.markdown("""
    1. التطبيق لا يطلب أي معلومات شخصية، ولا يتطلب إنشاء حساب، ولا يقوم بجمع أو تخزين أو الاحتفاظ بأي نصوص أو صور يقوم المستخدم برفعها على خوادم خاصة بالتطبيق.
    2. يتم معالجة النصوص والصور بشكل فوري عبر واجهة برمجة تطبيقات لأكثر من شركة عالمية موثوقة لتقديم خدمة الفحص.
    3. تخضع معالجة هذه البيانات لسياسة خصوصية Google.
    4. نقل البيانات يتم عبر بروتوكول آمن ومشفر (HTTPS).
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة المستخدم":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### ⚖️ سياسة المستخدم")
    st.write("يرجى قراءة بنود وسياسة استخدام التطبيق بعناية:")
    st.markdown("""
    1. النتائج يتم توليدها عبر تقنيات الذكاء الاصطناعي، والتطبيق غير مسؤول عن أي عدم دقة في النتائج، أو معلومات مغلوطة، أو أي قرارات يتخذها المستخدم بناءً على الفحص.
    2. النتائج ليس لها أي علاقة مباشرة بشركة Meta وإنما نتائج تقريبية مبنية على معايير المجتمع الخاص بشركة Meta.
    3. يمنع استخدام التطبيق لفحص مواد تخالف القانون أو تنتهك حقوق الملكية الفكرية والآداب العامة.
    4. التطبيق مجاني للجميع، يحق للمستخدمين الاستفادة من خدماته المجانية في فحص النصوص والصور.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "عن التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### ℹ️ عن التطبيق")
    st.write("""
    هذا التطبيق تم برمجة وتطويره بواسطة **Sakhr AlHubaish** ليحقق أعلى فائدة لمستخدميه في فحص المنشورات النصية والصور على منصة Meta قبل نشرها، وذلك لأجل تجنب القيود التي تفرضها سياسة معايير المجتمع الخاصة بالشركة.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "راسل التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("### 📬 راسل التطبيق")
    st.write("""
    يسعدنا تلقي استفساراتكم وملاحظاتكم لتطوير التطبيق عبر مراسلتي على البريد الإلكتروني التالي:
    
    📧 **sakhrs545@gmail.com**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="custom-divider-dark">', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 0.85rem;'>تم تطوير النظام بواسطة Sakhr AlHubaish © 2026 | جميع الحقوق محفوظة</p>", unsafe_allow_html=True)
