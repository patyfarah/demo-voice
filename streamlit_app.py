import base64
import os
import streamlit as st
from google import genai
from google.genai import types
from streamlit_webrtc import webrtc_streamer
import io
import wave
import soundfile as sf
from google.cloud import speech

st.write("Click the button below to record your audio.")

# Function for recording and converting audio to text using Google Speech-to-Text API
def record_audio():
    audio_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
    if audio_file:
        audio_data = audio_file.read()
        # Transcription logic using Google Cloud Speech-to-Text API
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        response = client.recognize(config=config, audio=audio)
        
        transcribed_text = ""
        for result in response.results:
            transcribed_text += result.alternatives[0].transcript
        
        st.audio(audio_data)
        return transcribed_text
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
    audio_data = record_audio()  #
