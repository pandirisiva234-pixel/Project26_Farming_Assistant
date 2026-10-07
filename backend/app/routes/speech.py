from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import tempfile

from services.speech_service import speech_to_text


# ========================================================
# CREATE ROUTER
# ========================================================

router = APIRouter(
    prefix="/speech",
    tags=["Speech-to-Text"]
)


# ========================================================
# SPEECH TO TEXT ENDPOINT
# ========================================================

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):

    # ====================================================
    # CHECK FILE
    # ====================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided"
        )


    # ====================================================
    # ALLOWED AUDIO FORMATS
    # ====================================================

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


    # ====================================================
    # SAVE TEMPORARY AUDIO FILE
    # ====================================================

    temp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp:

            temp_file = temp.name

            contents = await file.read()

            temp.write(contents)


        # =================================================
        # TRANSCRIBE AUDIO
        # =================================================

        result = speech_to_text(
            temp_file
        )


        # =================================================
        # CHECK TRANSCRIPTION ERROR
        # =================================================

        if result.get("error"):

            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )


        # =================================================
        # RETURN RESULT
        # =================================================

        return {
            "filename": file.filename,
            "text": result["text"],
            "detected_language": result["language"],
            "language_probability": result[
                "language_probability"
            ]
        }


    finally:

        # =================================================
        # DELETE TEMPORARY FILE
        # =================================================

        if temp_file and os.path.exists(temp_file):

            os.remove(temp_file)