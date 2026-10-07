from faster_whisper import WhisperModel


# ========================================================
# LOAD WHISPER MODEL
# ========================================================

MODEL_SIZE = "small"

print("Loading Whisper model...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper model loaded successfully.")


# ========================================================
# SPEECH TO TEXT
# ========================================================

def speech_to_text(audio_file: str):

    try:

        segments, info = model.transcribe(
            audio_file,
            beam_size=5
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }

    except Exception as e:

        print("Speech recognition error:", e)

        return {
            "text": "",
            "language": None,
            "language_probability": 0,
            "error": str(e)
        }