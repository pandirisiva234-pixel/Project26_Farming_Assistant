import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# ========================================================
# MODEL
# ========================================================

MODEL_NAME = "facebook/nllb-200-distilled-600M"


# ========================================================
# DEVICE
# ========================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ========================================================
# LANGUAGE CODES
# ========================================================

LANGUAGE_MAP = {
    # ================================================
    # INDIAN LANGUAGES
    # ================================================

    "en": "eng_Latn",   # English
    "te": "tel_Telu",   # Telugu
    "hi": "hin_Deva",   # Hindi
    "kn": "kan_Knda",   # Kannada
    "ta": "tam_Taml",   # Tamil
    "ml": "mal_Mlym",   # Malayalam
    "mr": "mar_Deva",   # Marathi
    "bn": "ben_Beng",   # Bengali
    "gu": "guj_Gujr",   # Gujarati
    "pa": "pan_Guru",   # Punjabi
    "or": "ory_Orya",   # Odia
    "as": "asm_Beng",   # Assamese

    # ================================================
    # FOREIGN LANGUAGES
    # ================================================

    "fr": "fra_Latn",   # French
    "es": "spa_Latn",   # Spanish
    "de": "deu_Latn",   # German
    "ar": "arb_Arab"    # Arabic
}


# ========================================================
# LOAD TOKENIZER
# ========================================================

print("Loading NLLB tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    src_lang="eng_Latn"
)


# ========================================================
# LOAD MODEL
# ========================================================

print("Loading NLLB model...")

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

model = model.to(DEVICE)

model.eval()


print("NLLB translation service ready.")
print("Device:", DEVICE)


# ========================================================
# TRANSLATE TEXT
# ========================================================

def translate_text(
    text: str,
    target_language: str = "en"
) -> str:

    if not text:
        return text

    if target_language == "en":
        return text

    if target_language not in LANGUAGE_MAP:
        print(
            f"Unsupported language: {target_language}"
        )
        return text

    target_code = LANGUAGE_MAP[target_language]

    try:

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        inputs = {
            key: value.to(DEVICE)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            translated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                    target_code
                ),
                max_length=512,
                num_beams=5
            )

        translated_text = tokenizer.batch_decode(
            translated_tokens,
            skip_special_tokens=True
        )[0]

        return translated_text

    except Exception as e:

        print(
            "Translation error:",
            str(e)
        )

        return text