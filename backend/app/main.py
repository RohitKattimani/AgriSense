import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import diagnose, field_scan, market, advisor, chat, outbreak, translate, qa

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AgriSense AI - Farm Companion API",
    description="Crop health diagnosis, market pricing, weather-aware sell/hold advice, "
                "and community tools for smallholder farmers.",
    version="1.0.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnose.router)
app.include_router(field_scan.router)
app.include_router(market.router)
app.include_router(advisor.router)
app.include_router(chat.router)
app.include_router(outbreak.router)
app.include_router(translate.router)
app.include_router(qa.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_provider": __import__("app.services.llm_service", fromlist=["llm_service"]).llm_service.provider,
    }
