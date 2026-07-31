from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services import vision_model, llm_service

router = APIRouter(prefix="/api/diagnose", tags=["diagnose"])


class DiagnoseResponse(BaseModel):
    top_label: str
    top_confidence: float
    crop: str
    condition: str
    is_healthy: bool
    predictions: list
    remedy_hint: str
    model_source: str
    explanation: str


@router.post("", response_model=DiagnoseResponse)
async def diagnose(
    image: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    notes: Optional[str] = Form(None),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image file (jpg/png).")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(400, "Uploaded image is empty.")

    result = vision_model.classify_image(image_bytes)

    system_prompt = (
        "You are AgriSense, a friendly agronomist explaining a plant disease diagnosis "
        "to a smallholder farmer with a basic smartphone. Use simple, warm, non-technical "
        "language (avoid jargon), keep it to 3-5 short sentences, and give 2-3 concrete "
        "next steps they can act on today. "
        + (f"Respond in {language}." if language and language != "en" else "")
    )
    user_msg = (
        f"Diagnosis: {result['condition']} on {result['crop']} "
        f"(confidence {result['top_confidence']:.0%}). "
        f"Reference remedy notes: {result['remedy_hint']}. "
        + (f"Farmer's notes: {notes}" if notes else "")
    )
    explanation = llm_service.llm_service.chat(system_prompt, user_msg)

    return DiagnoseResponse(**result, explanation=explanation)
