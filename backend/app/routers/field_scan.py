from collections import Counter
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services import vision_model, yield_estimator, llm_service

router = APIRouter(prefix="/api/field-scan", tags=["field-scan"])


@router.post("")
async def field_scan(
    images: List[UploadFile] = File(...),
    affected_area_pct: float = Form(30.0),
    language: Optional[str] = Form("en"),
):
    if not images:
        raise HTTPException(400, "Upload at least one image.")
    if len(images) > 20:
        raise HTTPException(400, "Max 20 photos per scan session.")

    results = []
    for img in images:
        content = await img.read()
        if not content:
            continue
        r = vision_model.classify_image(content)
        r["filename"] = img.filename
        results.append(r)

    if not results:
        raise HTTPException(400, "No valid images could be read.")

    total = len(results)
    healthy_count = sum(1 for r in results if r["is_healthy"])
    healthy_pct = round(100 * healthy_count / total, 1)

    condition_counts = Counter(r["condition"] for r in results if not r["is_healthy"])
    breakdown = [
        {"condition": cond, "count": cnt, "pct": round(100 * cnt / total, 1)}
        for cond, cnt in condition_counts.most_common()
    ]

    yield_loss = yield_estimator.estimate_field_yield_loss(results, affected_area_pct)

    dominant = breakdown[0]["condition"] if breakdown else "No disease"
    system_prompt = (
        "You are AgriSense, an agronomist summarizing a multi-plant field scan for a "
        "smallholder farmer. Be encouraging but honest, plain language, 4-6 sentences, "
        "and end with a clear priority action."
        + (f" Respond in {language}." if language and language != "en" else "")
    )
    user_msg = (
        f"Field scan of {total} plants: {healthy_pct}% healthy. "
        f"Top issue: {dominant}. Breakdown: {breakdown}. "
        f"Estimated yield loss: {yield_loss['estimated_yield_loss_pct']}%."
    )
    field_summary_text = llm_service.llm_service.chat(system_prompt, user_msg)

    return {
        "total_plants_scanned": total,
        "healthy_pct": healthy_pct,
        "field_health_score_pct": yield_loss["field_health_score_pct"],
        "condition_breakdown": breakdown,
        "yield_loss": yield_loss,
        "per_photo_results": results,
        "ai_summary": field_summary_text,
    }
