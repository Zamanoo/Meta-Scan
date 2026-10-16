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

# تنسيق CSS نظيف يضمن المحاذاة الكاملة من اليمين إلى اليسار (RTL)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
html, body, [class*='css'] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
}
.stTextInput, .stTextArea, .stSelectbox, .stMarkdown, h1, h2, h3, h4, h5, h6, p, div {
    direction: rtl;
    text-align: right;
}

/* إخفاء القائمة الجانبية تماماً لمنع التداخل */
[data-testid="stSidebar"] {
    display: none !important;
}

.main-header {
    background: linear-gradient(135deg, #0068c4 0%, #002b5c 100%);
    padding: 20px 15px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
.main-header h1 {
    font-size: 1.8rem;
    margin-bottom: 8px;
    text-align: center;
}
.main-header p {
    font-size: 0.9rem;
    margin: 0;
    text-align: center;
}
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 12px;
    direction: rtl;
    text-align: right;
}
.section-box {
    background-color: #f8f9fa;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #e9ecef;
    margin-bottom: 20px;
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
    font-size: 1rem;
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
    direction: rtl;
    text-align: right;
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
    GEMINI_KEYS = [st.secrets["GEMINI_KEY_1"], st.secrets["GEMINI_KEY_2"], st.secrets["GEMINI_KEY_3"], st.secrets["GEMINI_KEY_4"]]
except Exception as e:
    st.error("⚠️ تنبيه أمني: لم يتم العثور على المفاتيح السرية في إعدادات المنصة (Secrets).")
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
    raise Exception(f"نفدت الحصة لجميع مفاتيح Gemini. الخطأ الأخير: {last_error}")

# شريط التنقل العلوي المدمج
st.markdown("<h3 style='text-align: right;'>🛡️ META SCAN</h3>", unsafe_allow_html=True)
menu_option = st.selectbox(
    "اختر القسم:",
    [
        "الرئيسية", 
        "دليل معايير مجتمع Meta", 
        "سياسة الخصوصية", 
        "سياسة المستخدم", 
        "عن التطبيق", 
        "راسل التطبيق"
    ],
    label_visibility="collapsed"
)
st.markdown('<hr class="custom-divider-dark">', unsafe_allow_html=True)

if menu_option == "الرئيسية":
    st.markdown('<div class="main-header"><h1>🛡️ META SCAN</h1><p>النظام الذكي المتكامل لفحص النصوص والصور المرئية وتجنب قيود وحظر منصة ميتا</p></div>', unsafe_allow_html=True)

    # 1. قسم فحص نصوص المنشور
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ فحص نصوص المنشور</div>', unsafe_allow_html=True)
    
    post_content = st.text_area("نص المنشور:", height=120, placeholder="اكتب نص الإعلان أو المنشور هنا...", key="text_input_area")
    btn_text = st.button("🔍 افحص نص المنشور", key="btn_text_scan")

    if btn_text:
        if not post_content.strip():
            st.warning("⚠️ الرجاء كتابة نص المنشور أولاً.")
        else:
            found_local_words = [w for words in SUSPICIOUS_KEYWORDS.values() for w in words if w in post_content]
            with st.spinner("جاري التحليل العميق للسياق..."):
                try:
                    system_prompt = "أنت خبير محترف في سياسات وإعلانات منصات Meta. قم بتحليل النص المدخل بدقة، وبين مدى مطابقته للمعايير وسياسات المجتمع، وحدد الكلمات الحساسة واقترح تعديلات بديلة مضمونة الأمان."
                    completion = groq_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": post_content}], temperature=0.3, max_tokens=1024)
                    st.success("✅ تم فحص النص بنجاح!")
                    if found_local_words:
                        st.markdown(f'<div class="local-warning"><b>⚠️ تنبيه من المساعد المحلي:</b> تم رصد كلمات/مصطلحات حساسة في النص: <code>{", ".join(found_local_words)}</code></div>', unsafe_allow_html=True)
                    st.markdown("<h4 style='text-align: right;'>📊 تقرير تحليل النص:</h4>", unsafe_allow_html=True)
                    st.markdown(completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. قسم فحص صور المنشور
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼️ فحص صور المنشور</div>', unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("اختر ملف الصورة (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"], key="image_upload_area")

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة للفحص", use_column_width=True)
        btn_image = st.button("🔍 افحص صورة المنشور", key="btn_image_scan")
        if btn_image:
            with st.spinner("جاري تحليل الصورة..."):
                try:
                    prompt = "قم بتحليل هذه الصورة لإعلان تجاري لـ Meta. وضح هل تخالف السياسات وما هي التعديلات المطلوبة على التصميم لضمان قبوله."
                    res_text = analyze_image_with_fallback(image, prompt)
                    st.success("✅ تم تحليل الصورة بنجاح!")
                    st.markdown("<h4 style='text-align: right;'>📊 تقرير تحليل الصورة:</h4>", unsafe_allow_html=True)
                    st.markdown(res_text)
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء فحص الصورة: {e}")
    else:
        st.button("🔍 افحص صورة المنشور", key="btn_image_scan_disabled", disabled=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "دليل معايير مجتمع Meta":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📖 دليل معايير مجتمع Meta</div>', unsafe_allow_html=True)
    st.write("يعتمد فاحص **META SCAN** على تحليل المحتوى وفقاً لأبرز بنود السياسة والمعايير المعتمدة التالية من Meta:")
    st.markdown("""
    1. **العنف والتحريض:** منع الترويج للأعمال العنفية، التهديدات، أو الأسلحة.
    2. **خطاب الكراهية:** محاربة الهجوم على الأفراد أو المجموعات بناءً على العرق، الدين، الجنس.
    3. **المحتوى الجنسي والعري:** منع الترويج للصور أو العبارات الفاضحة.
    4. **الخطاب المضلل:** تجنب الأخبار المزيفة المؤثرة على السلامة العامة والانتخابات.
    5. **الملكية الفكرية:** حماية حقوق الملكية والقرصنة والعلامات التجارية.
    6. **المنتجات والخدمات المقيدة:** كالسلع المقيدة والعمليات المالية غير المرخصة.
    7. **الأمان والخصوصية:** منع مشاركة المعلومات الشخصية للآخرين (Doxxing).
    8. **التنمر والتحرش:** منع الإساءة المباشرة والمضايقات الرقمية.
    9. **الاحتيال والخداع:** منع الترويج للأنشطة المالية المشبوهة أو الوهمية.
    10. **السلع الخاضعة للرقابة:** الأدوية غير المرخصة والمواد المخدرة.
    11. **الانتحار أو إيذاء النفس:** منع تشجيع أو وصف وسائل إيذاء النفس.
    12. **التطرف والإرهاب:** حظر المنظمات الإرهابية والترويج لأفكارها.
    13. **التلاعب بالنظام (Spam):** نشر الروابط الوهمية والتفاعل الزائف.
    14. **الأخبار الصحية الزائفة:** تضليل الجمهور بشأن القضايا الصحية.
    15. **الاحتيال التجاري:** ضمان مصداقية العروض التجارية والإعلانات الممولة.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة الخصوصية":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔒 سياسة الخصوصية</div>', unsafe_allow_html=True)
    st.write("نحن نحترم خصوصيتك ونلتزم بحماية بياناتك الشخصية في تطبيق **META SCAN**:")
    st.markdown("""
    1. التطبيق لا يطلب أي معلومات شخصية ولا يتطلب إنشاء حساب ولا يقوم بتخزين أي نصوص أو صور.
    2. تتم معالجة النصوص والصور عبر واجهات برمجية آمنة وموثوقة.
    3. نقل البيانات يتم عبر بروتوكول مشفر (HTTPS).
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة المستخدم":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚖️ سياسة المستخدم</div>', unsafe_allow_html=True)
    st.write("يرجى قراءة بنود وسياسة استخدام التطبيق بعناية:")
    st.markdown("""
    1. النتائج يتم توليدها عبر الذكاء الاصطناعي والتطبيق غير مسؤول عن أي قرارات تتخذها بناءً عليها.
    2. النتائج تقريبية ومبنية على معايير Meta.
    3. يمنع استخدام التطبيق لفحص مواد تخالف القانون أو الآداب العامة.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "عن التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ عن التطبيق</div>', unsafe_allow_html=True)
    st.write("تم برمجة وتطوير هذا التطبيق بواسطة **Sakhr AlHubaish** لمساعدة المستخدمين في فحص المنشورات والإعلانات لتجنب قيود Meta.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "راسل التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📬 راسل التطبيق</div>', unsafe_allow_html=True)
    st.write("يسعدنا تلقي استفساراتكم وملاحظاتكم عبر البريد الإلكتروني:\n\n📧 **sakhrs545@gmail.com**")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="custom-divider-dark">', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 0.85rem;'>تم تطوير النظام بواسطة Sakhr AlHubaish © 2026 | جميع الحقوق محفوظة</p>", unsafe_allow_html=True)
