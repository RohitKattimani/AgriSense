from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services import llm_service

router = APIRouter(prefix="/api/qa", tags=["qa"])

# In-memory community Q&A store, seeded with a few realistic examples.
# Swap for a real DB in production; the similarity-search logic stays the same.
QA_STORE: List[dict] = [
    {"id": 1, "question": "Why are my tomato leaves curling upward?",
     "answer": "Leaf curl is often from heat stress or irregular watering. Keep soil evenly moist, mulch to retain moisture, and check the underside of leaves for pests like aphids.", "crop": "tomato"},
    {"id": 2, "question": "What is the best time to sell onions after harvest?",
     "answer": "Onion prices usually firm up 3-4 weeks after the main harvest glut passes, once wet/immature bulbs are out of the market - if you can store them dry and ventilated, waiting often pays off.", "crop": "onion"},
    {"id": 3, "question": "My potato plants have brown spots with a musty smell, what should I do?",
     "answer": "That sounds like late blight, especially in humid weather. Remove and destroy affected plants immediately to stop spread, and avoid watering the foliage directly.", "crop": "potato"},
    {"id": 4, "question": "How much water does wheat need per week during grain filling?",
     "answer": "During grain filling, wheat generally needs about 25-35mm of water per week depending on soil type and temperature - avoid water stress in this stage as it directly cuts grain weight.", "crop": "wheat"},
    {"id": 5, "question": "Is it normal for grape leaves to develop white powder on them?",
     "answer": "That's likely powdery mildew, common in warm, dry days with cool nights. Improve airflow by pruning, and apply sulfur-based fungicide early before it spreads to fruit.", "crop": "grapes"},
]
_next_id = 6


class NewQuestion(BaseModel):
    question: str
    crop: Optional[str] = None
    language: str = "en"


@router.get("")
def list_questions():
    return {"questions": QA_STORE}


@router.post("/ask")
def ask_question(req: NewQuestion):
    global _next_id

    similar = []
    if QA_STORE:
        corpus = [q["question"] for q in QA_STORE] + [req.question]
        vec = TfidfVectorizer().fit_transform(corpus)
        sims = cosine_similarity(vec[-1], vec[:-1]).flatten()
        ranked = sorted(zip(QA_STORE, sims), key=lambda p: -p[1])
        similar = [{**q, "similarity": round(float(s), 3)} for q, s in ranked[:3] if s > 0.05]

    system_prompt = (
        "You are AgriSense's community Q&A assistant. Answer the farmer's question "
        "clearly and practically in 2-4 sentences, using simple language. If similar "
        "past community answers are provided, use them as helpful context but tailor "
        "the answer to the new question."
        + (f" Respond in {req.language}." if req.language != "en" else "")
    )
    context = "\n".join(f"- Q: {s['question']} A: {s['answer']}" for s in similar) if similar else "None found."
    user_msg = f"New question: {req.question}\n\nSimilar past Q&A:\n{context}"
    ai_answer = llm_service.llm_service.chat(system_prompt, user_msg)

    entry = {"id": _next_id, "question": req.question, "answer": ai_answer, "crop": req.crop, "ai_generated": True}
    QA_STORE.append(entry)
    _next_id += 1

    return {"new_entry": entry, "similar_past_questions": similar}
