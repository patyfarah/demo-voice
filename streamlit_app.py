import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from streamlit_webrtc import webrtc_streamer

# Use webrtc_streamer to access the microphone
webrtc_streamer(key="example", audio_receiver_size=1024)

gemini_api_key = st.secrets["GeminiAI_Key"]


def generate(input_text, platform):
    client = genai.Client(
        api_key=gemini_api_key,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]

    # Platform-specific configurations
    platform_config = {
        "X": {
            "max_tokens": 280,
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
        system_instruction=[
            types.Part.from_text(
                text=selected_config.get("instruction", "")
            ),
        ],
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
    body {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("أداة لخلق محتوى بيئي لمنصات التواصل الاجتماعي")

# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:")

# Voice recording
st.subheader("أو قم بتسجيل ملاحظة صوتية")
if st.button("تسجيل صوت"):
    recorded_text = record_audio()
    if recorded_text:
        input_text = recorded_text
        st.text_area("النص المستخرج من الصوت:", value=recorded_text, height=100)

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
