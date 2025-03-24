import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from audio_recorder_streamlit import audio_recorder
import whisper
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()

gemini_api_key = st.secrets["GeminiAI_Key"]

# GitHub credentials and repository info
repo_name = 'patyfarah/social-media-ar'
token = 'patyfarah-access-token'
branch = 'main'  # Default branch (usually 'main' or 'master')

# Frontend for the application
def frontend():
    status_placeholder = st.empty()
    status_placeholder.write("سجل الموضوع بصوتك.")

    # Record audio input
    recorded_audio = audio_recorder(sample_rate=8000)

    # Handle the recorded audio
    if recorded_audio:
        st.audio(recorded_audio, format="audio/wav")
        st.write("Recording complete! Uploading to GitHub...")

        # Save the audio to a file locally
        audio_path = 'temp_audio.wav'
        with open(audio_path, 'wb') as f:
            f.write(recorded_audio)

        # Upload to GitHub
        #upload_audio_to_github(audio_path, repo_name, 'audio/temp_audio.wav', token, branch)

        #st.write("Audio uploaded successfully to GitHub!")

        # Transcribe the audio to text (Whisper)
        transcription = audio_to_text("temp_audio.wav")
        status_placeholder.write("Transcription completed.")

        # Display the transcription in the input area
        st.text_area("Transcription", transcription, height=200)

# Function to convert audio data to a file
def data_to_file(recorded_audio):
    temp_audio_path = "temp_audio.wav"
    with open(temp_audio_path, "wb") as temp_file:
        temp_file.write(recorded_audio)

    # Check if the file exists and is a valid audio file
    if os.path.exists(temp_audio_path):
        print(f"Audio file saved at: {temp_audio_path}")
    else:
        print(f"Failed to save audio file at: {temp_audio_path}")
    
    return temp_audio_path

def preprocess_audio(audio_path):
    # Load the audio file (convert MP3 to WAV for compatibility)
    audio = AudioSegment.from_file(audio_path)

    # Export it as a WAV file (You can change format if necessary)
    processed_audio_path = "processed_audio.wav"
    audio.export(processed_audio_path, format="wav")

    return processed_audio_path
    
# Function to transcribe audio to text using Whisper
def audio_to_text(audio_path):
    # Load the Whisper model (use the smallest model for Streamlit Cloud)
    model = whisper.load_model("small")  # You can choose 'base', 'small', 'medium', or 'large'
    
    # Transcribe the audio file
    result = model.transcribe(audio_path, language="ar")  # 'ar' for Arabic transcription, 'en' for English

    return result["text"]

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
# Run the frontend function
frontend()
# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:")

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
