from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from functools import partial

from app.services import price_model, weather_service, llm_service

router = APIRouter(prefix="/api/advisor", tags=["advisor"])


class AdvisorRequest(BaseModel):
    crop: str
    lat: float = 12.9716
    lon: float = 77.5946
    quantity_kg: float | None = None
    language: str = "en"


TOOLS_SCHEMA = [
    {
        "name": "get_price_trend",
        "description": "Get the recent price history, regression trend and 7-day price forecast for a crop.",
        "parameters": {
            "type": "object",
            "properties": {"crop": {"type": "string", "description": "Crop name, e.g. tomato"}},
            "required": ["crop"],
        },
    },
    {
        "name": "get_weather_forecast",
        "description": "Get a 5-day weather forecast for the farmer's location, including rain probability.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number"},
                "lon": {"type": "number"},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_perishability",
        "description": "Get how many days a crop can be safely stored before it starts to spoil/lose value.",
        "parameters": {
            "type": "object",
            "properties": {"crop": {"type": "string"}},
            "required": ["crop"],
        },
    },
]


def _tool_price_trend(crop: str = "tomato"):
    return price_model.get_trend(crop)


def _tool_weather(lat: float = 12.9716, lon: float = 77.5946):
    return weather_service.get_forecast(lat, lon)


def _tool_perishability(crop: str = "tomato"):
    crop = crop.lower()
    cfg = price_model.CROPS.get(crop, {"shelf_life_days": 7})
    return {"crop": crop, "shelf_life_days": cfg["shelf_life_days"]}


@router.post("/sell-hold")
def sell_hold(req: AdvisorRequest):
    crop = req.crop.lower()
    if crop not in price_model.CROPS:
        raise HTTPException(404, f"Unknown crop '{crop}'. Available: {price_model.list_crops()}")

    tool_impls = {
        "get_price_trend": partial(_tool_price_trend, crop=crop),
        "get_weather_forecast": partial(_tool_weather, lat=req.lat, lon=req.lon),
        "get_perishability": partial(_tool_perishability, crop=crop),
    }

    system_prompt = (
        "You are AgriSense's market advisor agent for smallholder farmers. "
        "You have tools to check the crop's price trend, the local weather forecast, "
        "and how perishable the crop is. ALWAYS call all three tools before answering. "
        "Then give a clear final recommendation starting with either 'SELL NOW' or "
        "'HOLD for N days', followed by a short, plain-language explanation (3-4 sentences) "
        "a farmer with no finance background can understand. Mention the price trend, "
        "any rain risk, and the shelf life as your reasons."
        + (f" Respond in {req.language}." if req.language != "en" else "")
    )
    qty_note = f" The farmer has {req.quantity_kg}kg ready to sell." if req.quantity_kg else ""
    user_message = f"Should I sell my {crop} now or hold?{qty_note}"

    agent_result = llm_service.llm_service.run_agent(
        system_prompt=system_prompt,
        user_message=user_message,
        tools=TOOLS_SCHEMA,
        tool_impls=tool_impls,
    )

    return {
        "crop": crop,
        "recommendation_text": agent_result["final_text"],
        "tool_calls": agent_result["tool_calls"],
    }
