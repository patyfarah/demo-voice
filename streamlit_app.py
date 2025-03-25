import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
from groq import Groq
import edge_tts
import asyncio

gemini_api_key = st.secrets["GeminiAI_Key"]
Groq_API_key = st.secrets["Groq_API_key"]

# Front end using streamlit
def frontend():
    status_placeholder = st.empty()
    status_placeholder.write("سجل الموضوع بصوتك")

    recorded_audio = audio_recorder(sample_rate=8000)

    # Handle user input
    if recorded_audio:
        status_placeholder.write("تسجيل الموضوع...")
        data_to_file(recorded_audio)
        status_placeholder.write("حفظ التسجيل...")
        transcription = audio_to_text("temp_audio.wav")
        status_placeholder.write("ترجمة التسجيل.")
        return transcription
        
# Function to convert audio data to audio file
def data_to_file(recorded_audio):
    temp_audio_path = "temp_audio.wav"
    with open(temp_audio_path, "wb") as temp_file:
        temp_file.write(recorded_audio)

# Function for audio to Arabic text translation
def audio_to_text(audio_path):
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

# Streamlit app
st.set_page_config(layout="centered", initial_sidebar_state="auto", page_title="أداة لخلق محتوى بيئي")

st.markdown(
    """
    <style>
    @font-face {
    font-family: 'CustomArabicFont';
    src: url('path-to-font-file.ttf');
    body {
        direction: rtl;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("أداة لخلق محتوى بيئي لمنصات التواصل الاجتماعي")
# Run the frontend function
a = frontend()
# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:",a)

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
