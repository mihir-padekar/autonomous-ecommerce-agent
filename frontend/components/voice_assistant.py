# Voice Assistant Component
# - Speech to Text  : st.audio_input() + Google Speech API
# - Text to Speech  : Browser's built-in SpeechSynthesis API


import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import io



# SPEECH TO TEXT
# Records audio from the mic and returns the transcribed text.


def render_voice_input() -> str | None:
    """
    Shows a mic recording widget.
    Returns the transcribed text string, or None if nothing spoken yet.

    Usage in chatbot.py:
        from components.voice_assistant import render_voice_input
        spoken_text = render_voice_input()
        if spoken_text:
            # treat it like the user typed this in the chat box
    """

    st.markdown(
        "<div style='font-size:12px; color:#94A3B8; margin-bottom:4px;'>"
        "🎤 Click the mic, speak, then click Stop</div>",
        unsafe_allow_html=True
    )

    # st.audio_input — built into Streamlit 1.29+
    # Records from the browser mic and returns WAV bytes
    audio_input = st.audio_input(
        label="Voice Input",
        label_visibility="collapsed",
        key="voice_mic_input"
    )

    if audio_input is not None:
        current_audio = audio_input.getvalue()
        previous_audio = st.session_state.get("voice_mic_audio_bytes")

        if previous_audio is None or current_audio != previous_audio:
            st.session_state.voice_mic_audio_bytes = current_audio
            st.session_state.voice_mic_processed = False
            st.session_state.voice_mic_transcript = None

            with st.spinner("🔄 Converting speech to text..."):
                try:
                    recognizer = sr.Recognizer()

                    # Wrap the raw bytes in a BytesIO so AudioFile can read it
                    audio_bytes = io.BytesIO(current_audio)

                    with sr.AudioFile(audio_bytes) as source:
                        # Adjust for background noise before recording
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio_data = recognizer.record(source)

                    # Uses Google's free STT API
                    text = recognizer.recognize_google(audio_data)  # type: ignore[attr-defined]
                    st.session_state.voice_mic_transcript = text

                except sr.UnknownValueError:
                    st.warning("⚠️ Could not understand. Please speak more clearly.")
                    st.session_state.voice_mic_transcript = None

                except sr.RequestError:
                    st.error("❌ Speech service unavailable. Check your internet connection.")
                    st.session_state.voice_mic_transcript = None

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.voice_mic_transcript = None

        transcript = st.session_state.get("voice_mic_transcript")
        already_processed = st.session_state.get("voice_mic_processed", False)

        if transcript and not already_processed:
            st.session_state.voice_mic_processed = True
            return transcript

    return None



# TEXT TO SPEECH
# Uses the browser's built-in SpeechSynthesis.


def speak_text(text: str, rate: float = 1.0, pitch: float = 1.0):
    """
    Speaks the given text aloud using the browser's SpeechSynthesis API.
    Runs entirely in the browser — no Python TTS library needed.

    Parameters:
        text  : the string to speak
        rate  : speech speed (0.5 = slow, 1.0 = normal, 1.5 = fast)
        pitch : voice pitch (0.5 = low, 1.0 = normal, 1.5 = high)

    Usage:
        from components.voice_assistant import speak_text
        speak_text("3 critical orders found. Escalation triggered.")
    """

    # Escape single/double quotes so JS doesn't break
    safe_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')

    components.html(
        f"""
        <script>
            // Cancel any speech already playing
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance('{safe_text}');
            utterance.rate  = {rate};
            utterance.pitch = {pitch};
            utterance.lang  = 'en-US';

            // Use a natural-sounding voice if available
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v =>
                v.name.includes('Google') || v.name.includes('Natural')
            );
            if (preferred) utterance.voice = preferred;

            window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0   # invisible — only runs the JS
    )



# VOICE STATUS INDICATOR
# Small animated dot shown in the chatbot panel header.


def render_voice_status(is_speaking: bool = False):
    """Renders a small status pill showing voice assistant state."""

    if is_speaking:
        html = """
        <div style="display:inline-flex; align-items:center; gap:6px;
                    background:#0F2A1A; border:1px solid #166534;
                    padding:4px 10px; border-radius:20px; font-size:11px; color:#4ADE80;">
            <span style="
                width:8px; height:8px; background:#4ADE80; border-radius:50%;
                animation: pulse 1s infinite;
            "></span>
            Speaking...
        </div>
        <style>
            @keyframes pulse {
                0%,100% { opacity:1; } 50% { opacity:0.3; }
            }
        </style>
        """
    else:
        html = """
        <div style="display:inline-flex; align-items:center; gap:6px;
                    background:#0F172A; border:1px solid #1E293B;
                    padding:4px 10px; border-radius:20px; font-size:11px; color:#94A3B8;">
            <span style="width:8px; height:8px; background:#4ADE80;
                         border-radius:50%;"></span>
            Voice Ready
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)