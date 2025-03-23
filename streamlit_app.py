import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from streamlit_webrtc import webrtc_streamer
import io
import wave
import soundfile as sf

# Upload an audio file (for playback purposes)
st.title("Audio Recorder in Streamlit Cloud")

st.write("Click the button below to record your audio.")

# Function for recording and converting audio to text (simple version using speech-to-text API)
def record_audio():
    audio_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
    if audio_file:
        audio_data = audio_file.read()
        # Transcription logic (mockup for now, you can use Google Speech API or similar here)
        st.audio(audio_data)
        return "This is the transcribed text from the audio."
    return ""

# Use HTML and JavaScript for audio recording in browser
record_button = st.button("Start Recording")

if record_button:
    # Replace the HTML code with a more functional audio recording feature
    audio_html = """
    <script>
        let rec;
        let audioStream;
        let audioChunks = [];
        
        function startRecording() {
            navigator.mediaDevices.getUserMedia({audio: true})
                .then(function(stream) {
                    audioStream = stream;
                    rec = new MediaRecorder(stream);
                    rec.ondataavailable = function(e) {
                        audioChunks.push(e.data);
                    };
                    rec.onstop = function() {
                        let audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                        let audioUrl = URL.createObjectURL(audioBlob);
                        let audio = new Audio(audioUrl);
                        audio.play();

                        // Send audio to Streamlit (via hidden iframe communication)
                        let reader = new FileReader();
                        reader.onload = function() {
                            let audioData = reader.result;
                            window.parent.postMessage({audio: audioData}, "*");
                        };
                        reader.readAsDataURL(audioBlob);
                    };
                    rec.start();
                    console.log("Recording...");
                });
        }

        function stopRecording() {
            rec.stop();
            audioStream.getTracks().forEach(track => track.stop());
            console.log("Recording stopped.");
        }

        document.getElementById("recordButton").onclick = function() {
            startRecording();
        };

        document.getElementById("stopButton").onclick = function() {
            stopRecording();
        };
    </script>
    <button id="recordButton">Start Recording</button>
    <button id="stopButton">Stop Recording</button>
    """

    # Display HTML
    st.markdown(audio_html, unsafe_allow_html=True)

    # Collecting the recorded audio and displaying it on Streamlit UI (mocked function)
    audio_data = record_audio()  # Here you would receive audio from the JS code (e.g., via a post message)
    if audio_data:
        st.audio(audio_data, format='audio/wav')


gemini_api_key = st.secrets["GeminiAI_Key"]


def generate(input_text, platform):
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
            types.Part.from_text(text=selected_config.get("instruction", ""))
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
