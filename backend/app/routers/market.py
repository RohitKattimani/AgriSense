from fastapi import APIRouter, HTTPException

from app.services import price_model

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/crops")
def crops():
    return {"crops": price_model.list_crops()}


@router.get("/trend/{crop}")
def trend(crop: str, n_days: int = 90, forecast_days: int = 7):
    try:
        return price_model.get_trend(crop, n_days=n_days, forecast_days=forecast_days)
    except ValueError as e:
        raise HTTPException(404, str(e))
