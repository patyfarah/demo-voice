import streamlit as st
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import io
import tempfile

# A custom audio processor for recording and processing the audio
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_data = None

    def recv(self, frame):
        # Convert audio frame to numpy array
        audio_np = np.array(frame.to_ndarray(), dtype=np.float32)
        if self.audio_data is None:
            self.audio_data = audio_np
        else:
            self.audio_data = np.concatenate((self.audio_data, audio_np), axis=0)
        return frame

    def get_audio_data(self):
        return self.audio_data

# Function to convert audio data to text using SpeechRecognition
def convert_audio_to_text(audio_data):
    recognizer = sr.Recognizer()
    if audio_data is None:
        return "No audio recorded"

    # Convert audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(audio_data.tobytes())
        tmpfile_path = tmpfile.name

    # Process the temporary audio file
    with sr.AudioFile(tmpfile_path) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

# Streamlit UI
st.title("أداة لخلق محتوى بيئي لمنصات التواصل الاجتماعي")

st.write("Click the button below to start recording audio.")

# Initialize the WebRTC streamer
webrtc_ctx = webrtc_streamer(key="audio-stream", 
                             audio_processor_factory=AudioProcessor,
                             mode=webrtc_streamer.WebRtcMode.SENDRECV)

if webrtc_ctx.state.playing:
    st.write("Recording audio...")

    # Wait for the audio to be processed
    audio_data = webrtc_ctx.audio_processor.get_audio_data()

    if audio_data is not None:
        # Convert the recorded audio data to text
        transcribed_text = convert_audio_to_text(audio_data)
        st.text_area("Extracted Text from Audio:", value=transcribed_text, height=100)

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

st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:")

# Voice recording
st.subheader("أو قم بتسجيل ملاحظة صوتية")
if st.button("تسجيل صوت"):
    if webrtc_ctx.state.playing:
        st.write("Recording in progress...")
    else:
        st.write("Press the button to start recording.")

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
