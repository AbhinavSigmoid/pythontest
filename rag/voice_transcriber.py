import io
import speech_recognition as sr


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Convert audio bytes (WAV format from st.audio_input)
    into a transcribed text string.

    Steps:
      1. Wrap raw bytes in a BytesIO buffer
      2. Feed into SpeechRecognition's AudioFile reader
      3. Call Google's free Web Speech API
      4. Return the recognised text (or an error message)

    Args:
        audio_bytes: Raw WAV bytes captured by st.audio_input()

    Returns:
        Transcribed text string, or an error/fallback string.
    """

    recognizer = sr.Recognizer()

    # Wrap bytes in a file-like object so SpeechRecognition can read it
    audio_file = io.BytesIO(audio_bytes)

    try:
        with sr.AudioFile(audio_file) as source:

            # Adjust for ambient noise (improves accuracy)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # Record the full audio from the file
            audio_data = recognizer.record(source)

        # Send to Google's free Web Speech API for transcription
        # No API key needed — uses the public endpoint
        text = recognizer.recognize_google(audio_data)

        return text

    except sr.UnknownValueError:
        # Audio was recorded but speech could not be understood
        return ""

    except sr.RequestError as e:
        # Network error or Google API unavailable
        return f"[Voice Error: Could not reach speech service — {e}]"

    except Exception as e:
        # Any other unexpected error
        return f"[Voice Error: {e}]"
