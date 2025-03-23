import streamlit as st
import io
import base64

# Import the necessary module for speech recognition (SpeechRecognition)
import speech_recognition as sr

st.write("Click the button below to record your audio.")

# Function for converting audio to text using SpeechRecognition (Free tool)
def convert_audio_to_text(audio_data):
    recognizer = sr.Recognizer()
    # Save the audio as a temporary file
    with open("temp.wav", "wb") as f:
        f.write(audio_data)

    # Use the SpeechRecognition library to convert audio to text
    with sr.AudioFile("temp.wav") as source:
        audio = recognizer.record(source)  # Read the entire audio file
        try:
            # Using the Google Web Speech API (free and built-in in SpeechRecognition)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

# Use HTML and JavaScript for audio recording in browser
record_button = st.button("Start Recording")

if record_button:
    # JavaScript code to enable audio recording in browser
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
    # Here, assume you will receive the audio through a post message.
    audio_data = ""  # Replace this with actual audio data received from JavaScript.

    if audio_data:
        # Convert the audio to text
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

st.title("أداة لخلق محتوى بيئي لمنصات التواصل الاجتماعي")

# Input fields
st.subheader("حدد الموضوع")
input_text = st.text_area("أدخل مضمون النص:")

# Voice recording
st.subheader("أو قم بتسجيل ملاحظة صوتية")
if st.button("تسجيل صوت"):
    recorded_text = convert_audio_to_text(audio_data)
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
