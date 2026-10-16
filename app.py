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

# CSS موحد ومستقر للثيم الداكن الدائم والعناوين الواضحة
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*='css'] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}

.stTextInput, .stTextArea, .stSelectbox, .stMarkdown, h1, h2, h3, h4, h5, h6, p, div {
    direction: rtl;
    text-align: right;
}

[data-testid="stSidebar"] {
    display: none !important;
}

.main-header {
    background: linear-gradient(135deg, #0068c4 0%, #002b5c 100%);
    padding: 12px 10px;
    border-radius: 10px;
    color: #ffffff !important;
    text-align: center;
    margin-bottom: 10px;
}
.main-header h1 {
    font-size: 1.4rem;
    margin-bottom: 4px;
    text-align: center;
    color: #ffffff !important;
}
.main-header p {
    font-size: 0.8rem;
    margin: 0;
    text-align: center;
    color: #e2e8f0 !important;
}

.section-box {
    background-color: #1e293b !important;
    padding: 12px 14px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    margin-bottom: 10px;
}

.section-title {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-bottom: 8px;
    direction: rtl;
    text-align: right;
}

.disclaimer-box {
    background-color: #1e293b !important;
    border-right: 4px solid #f59e0b !important;
    padding: 8px 12px;
    border-radius: 6px;
    margin-top: 2px;
    margin-bottom: 6px;
    font-size: 0.82rem;
    color: #cbd5e1 !important;
    direction: rtl;
    text-align: right;
    line-height: 1.4;
}
.disclaimer-title {
    font-weight: bold;
    color: #fbbf24 !important;
    margin-bottom: 2px;
    font-size: 0.85rem;
}

.stButton>button {
    width: 100% !important;
    background-color: #0068c4 !important;
    color: #ffffff !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    padding: 10px !important;
    border: none !important;
    font-size: 0.95rem !important;
    margin-top: 6px !important;
    display: block !important;
}
.stButton>button:hover {
    background-color: #004d99 !important;
}

.local-warning {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    padding: 8px 12px;
    border-radius: 8px;
    color: #856404;
    margin-top: 8px;
    font-size: 0.85rem;
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# 1. تهيئة Groq لفحص النصوص
try:
    groq_key = st.secrets["GROQ_API_KEY"]
    groq_client = Groq(api_key=groq_key)
except Exception as e:
    st.error("⚠️ تنبيه أمني: لم يتم العثور على المفتاح السري GROQ_API_KEY في إعدادات المنصة (Secrets).")
    st.stop()

# 2. التقاط جميع مفاتيح Gemini تلقائياً بغض النظر عن الأرقام أو الأسماء
gemini_keys = []
for k in st.secrets.keys():
    if "GEMINI" in k.upper():
        val = st.secrets[k]
        if isinstance(val, str) and val.strip():
            gemini_keys.append(val.strip())

if not gemini_keys:
    st.error("⚠️ تنبيه أمني: لم يتم العثور على أي مفتاح GEMINI في إعدادات المنصة (Secrets).")
    st.stop()

def analyze_image_with_gemini_rotation(image, prompt):
    global gemini_keys
    last_error = None
    
    for api_key in gemini_keys:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([image, prompt])
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            if "429" in str(e) or "ResourceExhausted" in str(e):
                continue
            else:
                continue
                
    raise Exception(f"تعذر معالجة الصورة بسبب نفاد حصة المفاتيح المتاحة: {last_error}")

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

if menu_option == "الرئيسية":
    st.markdown('<div class="main-header"><h1>🛡️ META SCAN</h1><p>النظام الذكي لفحص النصوص والإعلانات المرئية وتجنب الحظر</p></div>', unsafe_allow_html=True)

    # 1. قسم فحص نصوص المنشور (عبر Groq)
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ فحص نصوص المنشور</div>', unsafe_allow_html=True)
    
    post_content = st.text_area("نص المنشور:", height=80, placeholder="اكتب نص الإعلان أو المنشور هنا...", key="text_input_area", label_visibility="collapsed")
    btn_text = st.button("🔍 افحص نص المنشور", key="btn_text_scan")

    if btn_text:
        if not post_content.strip():
            st.warning("⚠️ الرجاء كتابة نص المنشور أولاً.")
        else:
            found_local_words = [w for words in SUSPICIOUS_KEYWORDS.values() for w in words if w in post_content]
            with st.spinner("جاري التحليل العميق للسياق عبر Groq..."):
                try:
                    system_prompt = "أنت خبير محترف في سياسات وإعلانات منصات Meta. قم بتحليل النص المدخل بدقة، وبين مدى مطابقته للمعايير وسياسات المجتمع، وحدد الكلمات الحساسة واقترح تعديلات بديلة مضمونة الأمان."
                    completion = groq_client.chat.completions.create(
                        model="openai/gpt-oss-20b", 
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": post_content}], 
                        temperature=0.3, 
                        max_tokens=1024
                    )
                    st.success("✅ تم فحص النص بنجاح عبر Groq!")
                    if found_local_words:
                        st.markdown(f'<div class="local-warning"><b>⚠️ تنبيه من المساعد المحلي:</b> تم رصد كلمات/مصطلحات حساسة في النص: <code>{", ".join(found_local_words)}</code></div>', unsafe_allow_html=True)
                    st.markdown("<h4 style='text-align: right; color: #ffffff;'>📊 تقرير تحليل النص:</h4>", unsafe_allow_html=True)
                    st.markdown(completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بنظام Groq: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. قسم فحص صور المنشور (عبر Gemini الذكي بالتبديل الآلي)
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼️ فحص صور المنشور</div>', unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("اختر ملف الصورة (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"], key="image_upload_area", label_visibility="collapsed")

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة للفحص", use_column_width=True)
        btn_image = st.button("🔍 افحص صورة المنشور", key="btn_image_scan")
        if btn_image:
            with st.spinner("جاري الفحص البصري العميق والتعرف على الشخصيات والعناصر عبر Gemini..."):
                try:
                    image_prompt = (
                        "أنت خبير فحص سياسات إعلانات ومعايير مجتمع Meta. "
                        "قم بتحليل هذه الصورة بدقة مطلقة واستخرج تفاصيلها: "
                        "1. من هو الشخص أو الشخصيات الموجودة في الصورة وهل هي شخصية عامة أو سياسية أو حساسة أو محظورة؟ "
                        "2. هل تحتوي الصورة على شعارات، رموز، أسلحة، أو نصوص تخالف سياسات Meta وتؤدي لحظر الحساب؟ "
                        "3. قدم تقييماً تفصيلياً لمدى أمان استخدام هذه الصورة في إعلان ممول مع اقتراح البدائل والتعديلات اللازمة."
                    )
                    res_text = analyze_image_with_gemini_rotation(image, image_prompt)
                    st.success("✅ تم الفحص البصري وإصدار التقرير بدقة عالية!")
                    st.markdown("<h4 style='text-align: right; color: #ffffff;'>📊 تقرير فحص الصورة والشخصيات:</h4>", unsafe_allow_html=True)
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

# عبارة إخلاء المسؤولية
st.markdown("""
<div class="disclaimer-box">
    <div class="disclaimer-title">تنويه إخلاء مسؤولية ⚠️</div>
    "هذه النتائج تقديرية مبنية على معايير المجتمع من شركة Meta وليس قرارًا رسميًا من Meta".
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: gray; font-size: 0.8rem; margin-top: 4px;'>تم تطوير النظام بواسطة Sakhr AlHubaish © 2026 | جميع الحقوق محفوظة</p>", unsafe_allow_html=True)
