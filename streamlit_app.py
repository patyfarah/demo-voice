import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from googletrans import Translator
import tempfile


gemini_api_key = st.secrets["GeminiAI_Key"]

# Streamlit app
st.set_page_config(layout="centered", initial_sidebar_state="expanded", page_title="أداة لخلق محتوى بيئي")

st.markdown(
    """
    <style>
    body {
        text-align: right;
        font-family:  Noto Sans Arabic,'Amiri',Arial, sans-serif;
        font-size: 24px;
        direction: rtl;
        unicode-bidi: embed;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Front end using streamlit
def speech_to_text_with_arabic_translation():
    """
    Captures speech from recorded audio, converts it to text, and translates it to Arabic.
    Uses audio-recorder-streamlit for audio capture.
    """
    translator = Translator()

    audio_bytes = audio_recorder()

    if audio_bytes:
        try:
            # Save the recorded audio to a temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Translate to Arabic
            translation = translator.translate(text, dest="ar")
            return translation.text

        except sr.UnknownValueError:
            st.error("Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            # Clean up the temporary audio file
            if 'temp_audio_path' in locals():
                os.remove(temp_audio_path)


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
a = speech_to_text_with_arabic_translation()
# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:", a)

# Platform selection
st.subheader("اختر المنصة")
platform = st.selectbox("اختر منصة التواصل الاجتماعي:", ["X", "Facebook", "LinkedIn"])

# Generate button
if st.button("جهز المحتوى"):
    with st.spinner("يتم انشاء المحتوى"):
        try:
            output = generate(input_text, platform)
            st.success("تم خلق المحتوى بنجاح!")
            st.text_area("مضمون المحتوى:", value=output, height=300)
        except Exception as e:
            st.error(f"خطأ: {e}")
