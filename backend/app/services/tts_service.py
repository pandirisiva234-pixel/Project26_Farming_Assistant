import edge_tts


# 16 supported project languages
VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "kn": "kn-IN-SapnaNeural",
    "ta": "ta-IN-PallaviNeural",
    "ml": "ml-IN-SobhanaNeural",
    "mr": "mr-IN-AarohiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "gu": "gu-IN-DhwaniNeural",
    "pa": "pa-IN-VaaniNeural",
    "or": "or-IN-SubhasiniNeural",
    "as": "as-IN-PriyankaNeural",

    # Foreign languages
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "de": "de-DE-KatjaNeural",
    "ar": "ar-SA-ZariyahNeural",
}


async def text_to_speech(
    text: str,
    language_code: str = "en",
    output_file: str = "output.mp3"
):

    if not text:
        return {
            "success": False,
            "error": "Text cannot be empty"
        }

    if language_code not in VOICE_MAP:
        return {
            "success": False,
            "error": f"Unsupported language: {language_code}"
        }

    voice = VOICE_MAP[language_code]

    try:

        communicate = edge_tts.Communicate(
            text,
            voice
        )

        await communicate.save(
            output_file
        )

        return {
            "success": True,
            "file": output_file,
            "language": language_code,
            "voice": voice
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }