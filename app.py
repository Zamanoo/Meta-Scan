import streamlit as st
import os
import re
import base64
from io import BytesIO
from groq import Groq
import requests
from PIL import Image

st.set_page_config(page_title="Post SCAN", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

SUSPICIOUS_KEYWORDS = {
    "financial": [
        "ربح سريع", "ثراء فاحش", "ضعف أموالك", "استثمار مضمون", "بدون مجهود", 
        "دخل اضافي مضمون", "قرض fوري بدون ضمانات", "ربح مضمون 100%"
    ],
    "health": [
        "علاج سحري", "خسارة الوزن بدون ديّت", "نتيجة مضمونة خلال أيام", 
        "شفاء تام", "مرخص طبياً (بدون إثبات)", "دواء معجزة"
    ],
    "behavioral": [
        "اضغط هنا فوراً", "لا تفوت الفرصة", "الربح للجميع", "سارع قبل نفاد الكمية (وهمي)",
        "اكسب آلاف الدولارات يومياً"
    ],
    "political_and_sensitive": [
        "الحوثيون", "أنصار الله", "جماعة الحوثي", 
        "المجلس الانتقالي الجنوبي", 
        "الحوثيين", "الانقلابيون", "السيد حسن نصرالله", "الحرب في اليمن", "الهدنة", 
        "المعتقلون السياسيون", "عبدالملك الحوثي", "السجناء السياسيون", 
        "الاختفاء القسري", "الاعتقالات", "القمع", "صدام حسين السيد عبدالملك", "الاحتجاجات الشعبية", 
        "المظاهرات", "حسن نصر الله", "العصيان المدني", "عبدالملك الحوثي", "الحوثي", "تقسيم اليمن", "الانفصال", "انصار الله", 
        "الوحدة اليمنية", "القضية الجنوبية", "النفوذ الإيراني", "النفوذ السعودي", 
        "التجنيد", "التجنيد الإجباري", "الانظمة العربية", "انتهاكات حقوق الإنسان", 
        "فلسطين", "غزة", "شعار الصرخة", "الضفة الغربية", "القدس", "إسرائيل", "الاحتلال الإسرائيلي", 
        "المقاومة الفلسطينية", "حماس", "الجهة الإسلامية", "حزب الله", "حزب اللات", 
        "المقاومة المسلحة", "هتلر", "النازية", "القتال", "الاقتتال", "الحرب", "خامنئي",  
        "سحل", "الأسلحة النووية", "استشهاد", "الشهيد", "الموت لأمريكا", "السينوار", 
        "الموت لامريكا", "الموت لإسرائيل", "الموت لأسرائيل", "الموت لاسرائيل", 
        "اللعنة على اليهود", "اللعنه على اليهود"
    ]
}

def obfuscate_specific_words(text, forbidden_words):
    modified_text = text
    for word in forbidden_words:
        if word in modified_text:
            obfuscated = "ـ.ـ".join(list(word))
            modified_text = modified_text.replace(word, obfuscated)
            
    return modified_text

st.markdown("""
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#0068c4">
<link rel="apple-touch-icon" href="icon.png">

<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap');

html, body, [class*='css'] {
    font-family: 'Rubik', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    margin-top: -1.0rem !important; 
}

[data-testid="stHeader"], 
header, 
[data-testid="stStatusWidget"], 
div[class*="StatusWidget"], 
.stStatusWidget, 
[data-testid="stDecoration"],
#MainMenu, 
[data-testid="stMainMenu"],
button[kind="header"],
div[data-testid="stToolbar"],
button[aria-label="View fullscreen"],
button[title*="View fullscreen"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    width: 0px !important;
    opacity: 0 !important;
    pointer-events: none !important;
    position: absolute !important;
    z-index: -9999 !important;
}

[data-testid="stConnectionStatus"],
div[class*="stConnectionStatus"],
div[class*="connectionError"],
.element-container:has(iframe[title="streamlit_app"]),
div[class*="stNotification"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.stButton, 
.stButton > button, 
[data-testid="stFileUploader"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

.stTextInput, .stTextArea, .stSelectbox, .stMarkdown, h1, h2, h3, h4, h5, h6, p, div, button, input, textarea {
    font-family: 'Rubik', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

.stElementContainer {
    margin-bottom: -0.2rem !important;
}

.main-header {
    background: linear-gradient(135deg, #0068c4 0%, #002b5c 100%);
    padding: 12px 10px;
    border-radius: 10px;
    color: #ffffff !important;
    text-align: center !important;
    margin-bottom: 10px;
}
.main-header h1 {
    font-size: 1.4rem;
    font-weight: 800 !important;
    margin-bottom: 4px;
    text-align: center !important;
    color: #ffffff !important;
}
.main-header p {
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    margin: 0;
    text-align: center !important;
    color: #f8fafc !important;
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
}

.disclaimer-box {
    background-color: #1e293b !important;
    border-right: 4px solid #f59e0b !important;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 0 4px 0;
    font-size: 0.82rem;
    font-weight: 400 !important;
    color: #cbd5e1 !important;
    line-height: 1.4;
}
.disclaimer-title {
    font-weight: 700 !important;
    color: #fbbf24 !important;
    margin-bottom: 2px;
    font-size: 0.85rem;
}

.stButton>button {
    width: 100% !important;
    background-color: #0068c4 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 10px !important;
    border: none !important;
    font-size: 0.92rem !important;
    font-family: 'Rubik', sans-serif !important;
}
.stButton>button:hover {
    background-color: #004d99 !important;
    color: #ffffff !important;
}

[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 8px !important;
}
[data-testid="stHorizontalBlock"] > div {
    flex: 1 !important;
    min-width: 0 !important;
}

.local-warning {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    padding: 8px 12px;
    border-radius: 8px;
    color: #856404;
    margin-top: 8px;
    font-size: 0.85rem;
    font-weight: 500 !important;
}

.status-card {
    padding: 12px 16px;
    border-radius: 10px;
    font-weight: 700 !important;
    font-size: 1.1rem;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.status-safe {
    background-color: rgba(16, 185, 129, 0.15);
    border: 2px solid #10b981;
    color: #34d399 !important;
}

.status-warning {
    background-color: rgba(245, 158, 11, 0.15);
    border: 2px solid #f59e0b;
    color: #fbbf24 !important;
}

.status-danger {
    background-color: rgba(239, 68, 68, 0.15);
    border: 2px solid #ef4444;
    color: #f87171 !important;
}

.report-container {
    color: #f8fafc;
    line-height: 1.7;
    font-size: 0.95rem;
    font-weight: 400 !important;
}
.report-title-custom {
    color: #60a5fa !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin-top: 16px !important;
    margin-bottom: 6px !important;
    display: block !important;
}

.rtl-menu-content ol, .rtl-menu-content ul {
    padding-right: 1.5rem !important;
    padding-left: 0rem !important;
    margin-right: 0rem !important;
}
.rtl-menu-content li {
    margin-bottom: 6px !important;
    font-weight: 400 !important;
}

.preview-card {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px;
    margin: 6px 0 10px 0;
    text-align: center;
}
.preview-card img {
    max-width: 100%;
    max-height: 320px;
    border-radius: 6px;
    object-fit: contain;
    display: block;
    margin: 0 auto;
}

.footer-copyright {
    direction: ltr !important;
    text-align: left !important;
    width: 100% !important;
    margin-top: 2px !important;
    margin-bottom: 2px !important;
    padding: 0 !important;
}
.footer-copyright p {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    font-family: 'Rubik', sans-serif !important;
    text-align: left !important;
    margin: 0 !important;
    padding: 0 !important;
}
</style>

<script>
const cleanStreamlitElements = () => {
    try {
        const doc = window.parent.document;
        const selectors = [
            '[data-testid="stStatusWidget"]',
            '[data-testid="stManageApp"]',
            '[data-testid="stMainMenu"]',
            'div[class*="viewerBadge"]',
            'div[class*="StatusWidget"]',
            '.stStatusWidget',
            'footer',
            'header',
            '#MainMenu',
            '.stAppBadge',
            'button[kind="header"]',
            'div[data-testid="stToolbar"]',
            '[data-testid="stConnectionStatus"]',
            'div[class*="connectionError"]'
        ];
        selectors.forEach(selector => {
            doc.querySelectorAll(selector).forEach(el => {
                el.remove();
            });
        });
    } catch(e) {}
};
cleanStreamlitElements();
setInterval(cleanStreamlitElements, 15);

setInterval(() => {
    try {
        window.parent.postMessage({type: "streamlit:ping"}, "*");
    } catch(e) {}
}, 10000);
</script>
""", unsafe_allow_html=True)

if "text_result" not in st.session_state:
    st.session_state.text_result = None
if "image_result" not in st.session_state:
    st.session_state.image_result = None
if "text_counter" not in st.session_state:
    st.session_state.text_counter = 0
if "image_counter" not in st.session_state:
    st.session_state.image_counter = 0
if "user_post_text" not in st.session_state:
    st.session_state.user_post_text = ""

try:
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY not found")
    groq_client = Groq(api_key=groq_key)
except Exception:
    st.error("⚠️ تنبيه أمني: لم يتم العثور على المفتاح السري GROQ_API_KEY في إعدادات المنصة.")
    st.stop()

gemini_keys = []
try:
    for k, v in os.environ.items():
        if "GEMINI" in k.upper() and v and v.strip():
            clean_key = v.strip().replace("\n", "").replace("\r", "")
            if clean_key not in gemini_keys:
                gemini_keys.append(clean_key)
except Exception:
    pass

def analyze_image_with_gemini(image, prompt):
    if not gemini_keys:
        raise Exception("لا يوجد مفاتيح Gemini معرفة في إعدادات المنصة.")

    if image.mode != "RGB":
        image = image.convert("RGB")

    max_dimension = 1600
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    last_err = None
    # استخدام الإصدار المستقر v1 مع النماذج الرسمية المعتمدة
    candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash"]

    for api_key in gemini_keys:
        for model_name in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}}
                        ]
                    }
                ]
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=25)
                if response.status_code == 200:
                    res_json = response.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text_output = parts[0].get("text", "")
                            if text_output:
                                return text_output
                else:
                    last_err = f"HTTP {response.status_code}: {response.text}"
            except Exception as e:
                last_err = e
                continue

    raise Exception(f"فشل الاتصال بخدمة Gemini المباشرة: {last_err}")

def render_status_badge(text_content):
    if "STATUS: SAFE" in text_content or "حالة المحتوى: آمن" in text_content or "غير مخالف" in text_content and "STATUS: DANGER" not in text_content and "STATUS: WARNING" not in text_content:
        st.markdown('''
        <div class="status-card status-safe">
            <span>🟢 النتيجة: محتوى غير مخالف (آمن للنشر)</span>
            <span>✅</span>
        </div>
        ''', unsafe_allow_html=True)
    elif "STATUS: DANGER" in text_content or "حالة المحتوى: مخالف" in text_content or "نص مخالف" in text_content or "صورة مخالفة" in text_content:
        st.markdown('''
        <div class="status-card status-danger">
            <span>🔴 النتيجة: محتوى مخالف لسياسات Meta</span>
            <span>❌</span>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="status-card status-warning">
            <span>🟡 النتيجة: محتوى مشبوه (يتطلب تعديلات)</span>
            <span>⚠️</span>
        </div>
        ''', unsafe_allow_html=True)

def display_formatted_report(raw_text):
    clean_text = re.sub(r'STATUS:\s*(SAFE|WARNING|DANGER)', '', raw_text).strip()
    parts = re.split(r'(خلاصة الفحص والتقييم العام|التقرير التفصيلي والكلمات الحساسة|البديل الموصى به والمتوافق|فحص الشخصيات والعناصر المرئية|التوصيات والتعديلات المطلوبة)', clean_text)
    
    html_output = '<div class="report-container">'
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i+1].strip() if (i+1) < len(parts) else ""
        
        emoji = "📋"
        if "التفصيلي" in title or "الشخصيات" in title:
            emoji = "🔍" if "التفصيلي" in title else "👤"
        elif "البديل" in title or "التوصيات" in title:
            emoji = "💡"
            
        html_output += f'<div class="report-title-custom">{emoji} {title}</div>'
        html_output += f'<div style="margin-bottom: 12px;">{content}</div>'
        
    html_output += '</div>'
    st.markdown(html_output, unsafe_allow_html=True)

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
    st.markdown('<div class="main-header"><h1>🛡️ POST SCAN</h1><center><p>تطبيق فاحص المنشورات الذكي للتعرف على المخاطر المحتملة قبل النشر، أستناداً إلى معايير Meta</p></center></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ فحص نصوص المنشور</div>', unsafe_allow_html=True)

    dynamic_text_key = f"text_input_area_{st.session_state.text_counter}"
    
    post_content = st.text_area(
        "نص المنشور:", 
        value=st.session_state.user_post_text, 
        height=80, 
        placeholder="اكتب نص المنشور هنا ...", 
        key=dynamic_text_key, 
        label_visibility="collapsed"
    )
    st.session_state.user_post_text = post_content

    col_right, col_left = st.columns(2)
    
    with col_right:
        btn_text = st.button("🔍 افحص نص المنشور", key="btn_text_scan")
        
    with col_left:
        st.components.v1.html("""
        <button onclick="
            const textarea = window.parent.document.querySelector('textarea');
            if (textarea && textarea.value.trim() !== '') {
                navigator.clipboard.writeText(textarea.value).then(() => {
                    alert('✅ تم نسخ النص إلى الحافظة بنجاح!');
                }).catch(err => {
                    alert('❌ تعذر النسخ، يرجى السماح للمتصفح بالوصول للحافظة');
                });
            } else {
                alert('⚠️ صندوق الإدخال فارغ، لا يوجد نص لنسخه!');
            }
        " style="
            width: 100%;
            background-color: #0068c4;
            color: white;
            font-weight: 700;
            border-radius: 8px;
            padding: 10px;
            border: none;
            font-size: 0.92rem;
            cursor: pointer;
            margin-top: -10px;
            text-align: center;
            font-family: 'Rubik', sans-serif;
        " onmouseover="this.style.backgroundColor='#004d99'" onmouseout="this.style.backgroundColor='#0068c4'">
            📋 نسخ النص
        </button>
        """, height=44, scrolling=False)

    if btn_text:
        if not post_content.strip():
            st.warning("⚠️ الرجاء كتابة نص المنشور أولاً.")
        else:
            with st.spinner("جاري فحص النص يرجى الأنتظار قليلاً..."):
                try:
                    system_prompt = (
                        "أنت خبير محترف في سياسات وإعلانات منصات Meta.\n"
                        "قم بتحليل النص المدخل بدقة، ويجب أن تتضمن إجابتك التنسيق المباشر التالي في البداية تماماً:\n"
                        "إذا كان النص كاملاً آمن اكتب في السطر الأول: STATUS: SAFE\n"
                        "إذا كان يحتوي مخاطر وحظر مباشر اكتب في السطر الأول: STATUS: DANGER\n"
                        "إذا كان يحتوي كلمات محتملة للشك اكتب في السطر الأول: STATUS: WARNING\n\n"
                        "ثم اكتب التقرير بالهيكلية التالية:\n"
                        "خلاصة الفحص والتقييم العام:\n"
                        "(ملخص شامل وسريع عن حالة النص للقبول الإعلاني)\n\n"
                        "التقرير التفصيلي والكلمات الحساسة:\n"
                        "(فحص الكلمات الحساسة، السياق، والمخاطر المباشرة أو الخفية)\n\n"
                        "البديل الموصى به والمتوافق:\n"
                        "(صياغة بديلة آمنة ومضمونة 100% لتجنب أي رفض إعلاني)"
                    )

                    completion = groq_client.chat.completions.create(
                        model="openai/gpt-oss-20b", 
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": post_content}], 
                        temperature=0.3, 
                        max_tokens=1024
                    )

                    st.session_state.text_result = completion.choices[0].message.content
                    st.success("✅ تم فحص النص بنجاح!")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الاتصال بنظام الفحص: {e}")

    if st.session_state.text_result:
        raw_result = st.session_state.text_result
        render_status_badge(raw_result)

        found_local_words = [w for words in SUSPICIOUS_KEYWORDS.values() for w in words if w in st.session_state.user_post_text]
        if found_local_words:
            st.markdown(f'<div class="local-warning"><b>⚠️ تنبيه من المساعد المحلي:</b> تم رصد مصطلحات دقيقة محلياً: <code>{", ".join(found_local_words)}</code></div>', unsafe_allow_html=True)
            
            if st.button("✨ تشكيل وتعديل النص", key="btn_obfuscate_text"):
                obfuscated = obfuscate_specific_words(st.session_state.user_post_text, found_local_words)
                st.session_state.user_post_text = obfuscated
                st.session_state.text_counter += 1
                st.rerun()

        display_formatted_report(raw_result)

        if st.button("🔄 فحص نص جديد", key="reset_text_btn"):
            st.session_state.text_result = None
            st.session_state.user_post_text = ""
            st.session_state.text_counter += 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🖼️ فحص صور المنشور</div>', unsafe_allow_html=True)

    dynamic_image_key = f"image_upload_area_{st.session_state.image_counter}"
    uploaded_image = st.file_uploader("اختر ملف الصورة (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"], key=dynamic_image_key, label_visibility="collapsed")

    if uploaded_image:
        image = Image.open(uploaded_image)
        
        preview_img = image.convert("RGB") if image.mode != "RGB" else image

        buf = BytesIO()
        preview_img.save(buf, format="JPEG", quality=95)
        preview_base64 = base64.b64encode(buf.getvalue()).decode()

        st.markdown(f'''
        <div class="preview-card">
            <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 6px; text-align: right;">📷 معاينة الصورة المختارة:</p>
            <img src="data:image/jpeg;base64,{preview_base64}" alt="Preview" />
        </div>
        ''', unsafe_allow_html=True)

    btn_image = st.button("🔍 افحص صورة المنشور", key="btn_image_scan")

    if btn_image:
        if not uploaded_image:
            st.warning("⚠️ الرجاء اختيار صورة المنشور أولاً.")
        else:
            image = Image.open(uploaded_image)
            with st.spinner("جاري فحص الصورة عبر مساعد الذكاء الاصطناعي..."):
                try:
                    image_prompt = (
                        "أنت خبير فحص سياسات إعلانات ومعايير مجتمع Meta.\n"
                        "قم بتحليل الصورة بدقة عالية، ويجب وضع حالة النتيجة في السطر الأول تماماً كالتالي:\n"
                        "إذا كانت الصورة آمنة تماماً: STATUS: SAFE\n"
                        "إذا كانت الصورة تحتوي شخصية محظورة أو أسلحة أو رموز مخالفة: STATUS: DANGER\n"
                        "إذا كانت الصورة تحتوي تلميحات أو عناصر مشبوهة: STATUS: WARNING\n\n"
                        "ثم اكتب التقرير بوضوح:\n"
                        "خلاصة الفحص والتقييم العام\n"
                        "(ملخص شامل وسريع عن حالة الصورة للقبول الإعلاني)\n\n"
                        "فحص الشخصيات والعناصر المرئية\n"
                        "(فحص الوجوه، الشخصيات العامة أو السياسية، الأسلحة، الرموز والشعارات)\n\n"
                        "التوصيات والتعديلات المطلوبة\n"
                        "(إرشادات عمل لتعديل الصورة أو استبدالها لضمان الأمان)"
                    )

                    st.session_state.image_result = analyze_image_with_gemini(image, image_prompt)
                    st.success("✅ تم الفحص البصري بنجاح!")
                except Exception as e:
                    st.error(f"❌ تعذر معالجة الصورة عبر محرك الفحص: {e}")

    if st.session_state.image_result:
        res_text = st.session_state.image_result
        render_status_badge(res_text)

        display_formatted_report(res_text)

        if st.button("🔄 فحص صورة جديدة", key="reset_img_btn"):
            st.session_state.image_result = None
            st.session_state.image_counter += 1
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">تنويه إخلاء مسؤولية ⚠️</div>
        "هذه النتائج تقديرية مبنية على معايير المجتمع من شركة Meta وليس قرارًا رسميًا من Meta".
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-copyright">
        <p>Developed by Sakhr AlHubaish | Copyright 2026</p>
    </div>
    """, unsafe_allow_html=True)

elif menu_option == "دليل معايير مجتمع Meta":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📖 دليل معايير مجتمع Meta</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="rtl-menu-content">
        <p>يعتمد فاحص <b>POST SCAN</b> على تحليل المحتوى وفقاً لأبرز بنود السياسة والمعايير المعتمدة التالية من Meta:</p>
        <ol>
            <li><b>العنف والتحريض:</b> منع الترويج للأعمال العنفية، التهديدات، أو الأسلحة.</li>
            <li><b>خطاب الكراهية:</b> محاربة الهجوم على الأفراد أو المجموعات بناءً على العرق، الدين، الجنس.</li>
            <li><b>المحتوى الجنسي والعري:</b> منع الترويج للصور أو العبارات الفاضحة.</li>
            <li><b>الخطاب المضلل:</b> تجنب الأخبار المزيفة المؤثرة على السلامة العامة والانتخابات.</li>
            <li><b>الملكية الفكرية:</b> حماية حقوق الملكية والقرصنة والعلامات التجارية.</li>
            <li><b>المنتجات والخدمات المقيدة:</b> كالسلع المقيدة والعمليات المالية غير المرخصة.</li>
            <li><b>الأمان والخصوصية:</b> منع مشاركة المعلومات الشخصية للآخرين (Doxxing).</li>
            <li><b>التنمر والتحرش:</b> منع الإساءة المباشرة والمضايقات الرقمية.</li>
            <li><b>الاحتيال والخداع:</b> منع الترويج للأنشطة المالية المشبوهة أو الوهمية.</li>
            <li><b>السلع الخاضعة للرقابة:</b> الأدوية غير المرخصة والمواد المخدرة.</li>
            <li><b>الانتحار أو إيذاء النفس:</b> منع تشجيع أو وصف وسائل إيذاء النفس.</li>
            <li><b>التطرف والإرهاب:</b> حظر المنظمات الإرهابية والترويج لأفكارها.</li>
            <li><b>التلاعب بالنظام (Spam):</b> نشر الروابط الوهمية والتفاعل الزائف.</li>
            <li><b>الأخبار الصحية الزائفة:</b> تضليل الجمهور بشأن القضايا الصحية.</li>
            <li><b>الاحتيال التجاري:</b> ضمان مصداقية العروض التجارية والإعلانات الممولة.</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة الخصوصية":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔒 سياسة الخصوصية</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="rtl-menu-content">
        <p>نحن نحترم خصوصيتك ونلتزم بحماية بياناتك الشخصية في تطبيق <b>POST SCAN</b>:</p>
        <ol>
            <li>التطبيق لا يطلب أي معلومات شخصية ولا يتطلب إنشاء حساب ولا يقوم بتخزين أي نصوص أو صور.</li>
            <li>تتم معالجة النصوص والصور عبر واجهات برمجية آمنة وموثوقة.</li>
            <li>نقل البيانات يتم عبر بروتوكول مشفر (HTTPS).</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "سياسة المستخدم":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚖️ سياسة المستخدم</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="rtl-menu-content">
        <p>يرجى قراءة بنود وسياسة استخدام التطبيق بعناية:</p>
        <ol>
            <li>النتائج يتم توليدها عبر الذكاء الاصطناعي والتطبيق غير مسؤول عن أي قرارات تتخذها بناءً عليها.</li>
            <li>قد تحصل اخطأ أحياناً عند فحص النصوص والصور في حال كان هناك ضغط على نماذج فحص الذكاء الاصطناعي.</li>
            <li>النتائج تقريبية ومبنية على معايير Meta.</li>
            <li>يمنع استخدام التطبيق لفحص مواد تخالف القانون أو الآداب العامة.</li>
        </ol>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "عن التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ عن التطبيق</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="rtl-menu-content">
        <p>تم برمجة وتطوير هذا التطبيق بواسطة <b>Sakhr AlHubaish</b> لمساعدة المستخدمين في فحص المنشورات والإعلانات لتجنب قيود Meta.</p>
        <p>اصدار التطبيق v1.0 </p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu_option == "راسل التطبيق":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📬 راسل التطبيق</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="rtl-menu-content">
        <p>يسعدنا تلقي استفساراتكم وملاحظاتكم عبر البريد الإلكتروني:</p>
        <p>📧 <b>sakhrs545@gmail.com</b></p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
