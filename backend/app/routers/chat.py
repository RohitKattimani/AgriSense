from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.services import llm_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    language: str = "en"
    context: Optional[str] = None  # e.g. last diagnosis summary, injected for continuity


@router.post("")
def chat(req: ChatRequest):
    system_prompt = (
        "You are AgriSense, a warm, practical AI farm companion for smallholder farmers - "
        "part agronomist, part market analyst, part weather advisor. Keep answers short, "
        "concrete, and in simple everyday language. If you don't have enough information "
        "to be specific, ask one clarifying question."
        + (f" Respond in {req.language}." if req.language != "en" else "")
        + (f"\n\nRelevant context from earlier in this session: {req.context}" if req.context else "")
    )
    history = [{"role": m.role, "content": m.content} for m in req.history]
    reply = llm_service.llm_service.chat(system_prompt, req.message, history=history)
    return {"reply": reply}
