from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import tempfile
import uuid

from services.speech_service import speech_to_text
from services.intent_classifier import classify_intent
from services.rag_service import search_knowledge, extract_answer
from services.translation_service import translate_text
from services.tts_service import text_to_speech


router = APIRouter(
    prefix="/voice-assistant",
    tags=["Voice Assistant"]
)


# Folder for generated TTS audio
AUDIO_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "generated_audio"
)

os.makedirs(AUDIO_FOLDER, exist_ok=True)


# --------------------------------------------------
# Clean and shorten RAG answer
# --------------------------------------------------

def clean_answer(answer: str) -> str:

    if not answer:
        return "I could not find relevant agricultural information."

    # Remove extra spaces
    answer = answer.strip()

    # Split into lines
    lines = answer.splitlines()

    clean_lines = []
    seen_lines = set()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove duplicate lines
        normalized = " ".join(line.split()).lower()

        if normalized not in seen_lines:

            seen_lines.add(normalized)
            clean_lines.append(line)

    answer = "\n".join(clean_lines)

    # Limit very long answers
    MAX_LENGTH = 1000

    if len(answer) > MAX_LENGTH:

        answer = answer[:MAX_LENGTH]

        # Avoid cutting in the middle of a word
        last_space = answer.rfind(" ")

        if last_space > 500:
            answer = answer[:last_space]

        answer += "..."

    return answer


# --------------------------------------------------
# Voice Assistant API
# --------------------------------------------------

@router.post("/query")
async def voice_assistant_query(
    file: UploadFile = File(...),
    language_code: str = Form("en")
):

    # --------------------------------------------------
    # 1. Validate audio file
    # --------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )


    allowed_extensions = {
        ".wav",
        ".mp3",
        ".m4a",
        ".ogg",
        ".webm"
    }


    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                "Use WAV, MP3, M4A, OGG or WEBM."
            )
        )


    # --------------------------------------------------
    # 2. Validate language
    # --------------------------------------------------

    supported_languages = {
        "en",
        "te",
        "hi",
        "kn",
        "ta",
        "ml",
        "mr",
        "bn",
        "gu",
        "pa",
        "or",
        "as",
        "fr",
        "es",
        "de",
        "ar"
    }


    if language_code not in supported_languages:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language code: {language_code}"
        )


    temp_file = None


    try:

        # --------------------------------------------------
        # 3. Save uploaded audio temporarily
        # --------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp:

            temp_file = temp.name

            contents = await file.read()

            temp.write(contents)


        # --------------------------------------------------
        # 4. Speech-to-Text
        # --------------------------------------------------

        stt_result = speech_to_text(
            temp_file
        )


        if stt_result.get("error"):

            raise HTTPException(
                status_code=500,
                detail=stt_result["error"]
            )


        text = stt_result.get(
            "text",
            ""
        ).strip()


        if not text:

            raise HTTPException(
                status_code=400,
                detail="Could not recognize speech"
            )


        # --------------------------------------------------
        # 5. Intent Classification
        # --------------------------------------------------

        intent = classify_intent(
            text
        )


        # --------------------------------------------------
        # 6. RAG Knowledge Retrieval
        # --------------------------------------------------

        documents = search_knowledge(
            text,
            top_k=3
        )


        # --------------------------------------------------
        # 7. Generate agricultural answer
        # --------------------------------------------------

        if documents:

            english_answer = extract_answer(
                documents[0]
            )

        else:

            english_answer = (
                "I could not find relevant "
                "agricultural information."
            )


        # --------------------------------------------------
        # 8. Clean repeated / long answer
        # --------------------------------------------------

        english_answer = clean_answer(
            english_answer
        )


        # --------------------------------------------------
        # 9. Translate answer
        # --------------------------------------------------

        translated_answer = translate_text(
            english_answer,
            language_code
        )


        # --------------------------------------------------
        # 10. Clean translated answer
        # --------------------------------------------------

        translated_answer = translated_answer.strip()


        # --------------------------------------------------
        # 11. Generate TTS audio
        # --------------------------------------------------

        audio_filename = (
            f"response_{uuid.uuid4().hex}.mp3"
        )


        audio_path = os.path.join(
            AUDIO_FOLDER,
            audio_filename
        )


        tts_result = await text_to_speech(
            translated_answer,
            language_code,
            audio_path
        )


        if not tts_result.get("success"):

            raise HTTPException(
                status_code=500,
                detail=tts_result.get(
                    "error",
                    "Text-to-Speech failed"
                )
            )


        # --------------------------------------------------
        # 12. Return complete response
        # --------------------------------------------------

        return {

            "filename": file.filename,

            "speech_to_text": text,

            "detected_language":
                stt_result.get("language"),

            "language_probability":
                stt_result.get(
                    "language_probability"
                ),

            "intent": intent,

            "requested_language":
                language_code,

            "answer":
                translated_answer,

            "retrieved_documents":
                len(documents),

            "audio_file":
                audio_filename,

            "audio_path":
                f"/voice-assistant/audio/{audio_filename}"
        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "Voice Assistant Error:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    finally:

        # --------------------------------------------------
        # 13. Delete temporary uploaded audio
        # --------------------------------------------------

        if (
            temp_file
            and os.path.exists(temp_file)
        ):

            os.remove(
                temp_file
            )