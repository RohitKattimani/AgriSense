from fastapi import APIRouter
from pydantic import BaseModel

from app.services import llm_service

router = APIRouter(prefix="/api/translate", tags=["translate"])

# A small curated set to start with; any BCP-47-ish name works since the
# LLM handles the actual translation.
SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "Hindi", "kn": "Kannada", "ta": "Tamil",
    "te": "Telugu", "mr": "Marathi", "bn": "Bengali", "gu": "Gujarati",
    "pa": "Punjabi", "ml": "Malayalam",
}


class TranslateRequest(BaseModel):
    text: str
    target_language: str  # code from SUPPORTED_LANGUAGES


@router.get("/languages")
def languages():
    return SUPPORTED_LANGUAGES


@router.post("")
def translate(req: TranslateRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.target_language, req.target_language)
    if req.target_language == "en":
        return {"translated_text": req.text}
    system_prompt = (
        f"You are a translation engine. Translate the user's text into {lang_name}, "
        "in a natural, conversational tone suitable for a farmer. "
        "Return ONLY the translated text, nothing else."
    )
    translated = llm_service.llm_service.chat(system_prompt, req.text)
    return {"translated_text": translated, "target_language": lang_name}
