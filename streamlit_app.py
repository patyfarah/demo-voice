import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
from groq import Groq

gemini_api_key = st.secrets["GeminiAI_Key"]
Groq_API_key = st.secrets["Groq_API_key"]

# Streamlit app
st.set_page_config(layout="centered", initial_sidebar_state="expanded", page_title="أداة لخلق محتوى بيئي")

st.markdown(
    """
    <style>
    body {
        text-align: right;
        font-family:  Arial, sans-serif;
        font-size: 24px;
        direction: rtl;
        unicode-bidi: embed;
    }
    .rtl {
        direction: rtl;
        text-align: right;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# Front end using streamlit
def frontend():
    status_placeholder = st.empty()
    status_placeholder.write("سجل الموضوع بصوتك")

    # Record audio and store it in a variable
    recorded_audio = audio_recorder(sample_rate=8000)
    
    # Handle user input
    if recorded_audio:
        status_placeholder.write("تسجيل الموضوع...")
        data_to_file(recorded_audio)
        status_placeholder.write("حفظ التسجيل...")
        transcription = audio_to_text("temp_audio.wav")
        status_placeholder.write("ترجمة التسجيل.")
        return transcription

# Define helper functions
def data_to_file(audio_data):
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data)


def audio_to_text(audio_path):
    # Use the Groq client for transcription
    client = Groq(api_key=Groq_API_key)
    with open(audio_path, 'rb') as file:
        transcription = client.audio.translations.create(
            file=(audio_path, file.read()),
            model='whisper-large-v3'
        )
    return transcription.text


def generate(input_text, platform):
    """Generates content based on user input and platform."""
    client = genai.Client(
        api_key=gemini_api_key,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=input_text)],
        ),
    ]

    # Platform-specific configurations
    platform_config = {
        "X": {
            "max_tokens": 100,
            "instruction": "اعطني كخبير في مجال البيئة تغريدة لمنصة إكس، احصر إجابتك بالمواضيع البيئية فقط وعدد المقترح واحد، لا جواب إذا لم يكن الموضوع بيئيًا."
        },
        "Facebook": {
            "max_tokens": 500,
            "instruction": "كخبير في البيئة، اكتب منشورًا مناسبًا لمنصة فيسبوك عن الموضوع البيئي الذي أدخلته. يمكن أن يكون المنشور أطول ويحتوي على تفاصيل أكثر."
        },
        "LinkedIn": {
            "max_tokens": 700,
            "instruction": "كخبير بيئي، اكتب منشورًا محترفًا يناسب منصة لينكد إن عن الموضوع البيئي الذي أدخلته. ركز على التفاصيل والمعلومات الدقيقة."
        },
    }

    selected_config = platform_config.get(platform, {})

    generate_content_config = types.GenerateContentConfig(
        temperature=2,
        top_p=0.95,
        top_k=40,
        max_output_tokens=selected_config.get("max_tokens", 100),
        response_mime_type="text/plain",
        system_instruction=[types.Part.from_text(text=selected_config.get("instruction", ""))],
    )

    result = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        result += chunk.text
    return result



st.title("🧰أداة لخلق محتوى بيئي لمنصات التواصل الاجتماعي📀")

#Sidebar
# Sidebar information about you
st.sidebar.title("🧍‍♀️عن المبرمج")
st.sidebar.markdown("""
<div style= font-size: 24px;text-align: left;">
    مرحبًا، أنا باتي فرح، مطور وباحث في مجال الذكاء الاصطناعي ونظم المعلومات الجغرافية
    أعمل على بناء أدوات مبتكرة تساعد في تحسين النظم البيئية وجودة العمل الاداري
</div>

<div style="color: #008080; font-size: 16px; text-align: left; padding: 10px; border: 1px solid #008080; margin-top: 20px;">
    <strong>البريد الإلكتروني:</strong> farahpaty@hotmail.com
</div>
""", unsafe_allow_html=True)

# Run the frontend function
a = frontend()
# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:", a)

# Platform selection
st.subheader("اختر المنصة")
platform = st.selectbox("اختر منصة التواصل الاجتماعي:", ["X", "Facebook", "LinkedIn"])

# Generate button
if st.button("Generate"):
    with st.spinner("Generating content..."):
        try:
            output = generate(input_text, platform)
            st.success("تم خلق المحتوى بنجاح!")
            st.text_area("مضمون المحتوى:", value=output, height=300)
        except Exception as e:
            st.error(f"خطأ: {e}")
