from fastapi import APIRouter

from app.services import outbreak_service

router = APIRouter(prefix="/api/outbreak", tags=["outbreak"])


@router.get("/map")
def outbreak_map(eps_km: float = 2.0, min_samples: int = 4):
    return outbreak_service.get_outbreak_map(eps_km=eps_km, min_samples=min_samples)
