"""
Market price trend service.

Since live mandi/market APIs require paid access or region-specific
scraping, this module simulates realistic historical price data (seasonal
wave + random walk + noise) for a handful of crops, then fits a
regression model (linear trend + polynomial curve) to project short-term
price direction. This is the same interface a real data source (e.g.
Agmarknet, data.gov.in) could be swapped into later - only
`_simulate_history()` would need to change.
"""
from __future__ import annotations
import math
import random
from datetime import date, timedelta
from typing import Dict, List

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

CROPS: Dict[str, Dict] = {
    "tomato":  {"base_price": 18, "volatility": 2.5, "seasonal_amp": 4, "unit": "kg", "currency": "INR", "shelf_life_days": 5},
    "potato":  {"base_price": 14, "volatility": 1.2, "seasonal_amp": 2, "unit": "kg", "currency": "INR", "shelf_life_days": 30},
    "onion":   {"base_price": 22, "volatility": 3.5, "seasonal_amp": 6, "unit": "kg", "currency": "INR", "shelf_life_days": 25},
    "wheat":   {"base_price": 24, "volatility": 0.8, "seasonal_amp": 1.5, "unit": "kg", "currency": "INR", "shelf_life_days": 180},
    "grapes":  {"base_price": 55, "volatility": 5.0, "seasonal_amp": 10, "unit": "kg", "currency": "INR", "shelf_life_days": 3},
}


def _simulate_history(crop: str, n_days: int = 90) -> List[Dict]:
    cfg = CROPS[crop]
    rng = random.Random(hash(crop) % (2**32))
    prices = []
    price = cfg["base_price"]
    start = date.today() - timedelta(days=n_days)
    for i in range(n_days):
        d = start + timedelta(days=i)
        seasonal = cfg["seasonal_amp"] * math.sin(2 * math.pi * i / 30)
        drift = rng.gauss(0, cfg["volatility"] * 0.15)
        price = max(cfg["base_price"] * 0.4, price + drift + seasonal * 0.05)
        prices.append({"date": d.isoformat(), "price": round(price, 2)})
    return prices


def get_price_history(crop: str, n_days: int = 90) -> List[Dict]:
    crop = crop.lower()
    if crop not in CROPS:
        raise ValueError(f"Unknown crop '{crop}'. Available: {list(CROPS.keys())}")
    return _simulate_history(crop, n_days)


def get_trend(crop: str, n_days: int = 90, forecast_days: int = 7) -> Dict:
    """
    Fits a linear regression (overall trend / slope) and a degree-2
    polynomial regression (captures short-term curvature) to the simulated
    price history, then projects `forecast_days` ahead.
    """
    crop = crop.lower()
    history = get_price_history(crop, n_days)
    X = np.arange(len(history)).reshape(-1, 1)
    y = np.array([h["price"] for h in history])

    linreg = LinearRegression().fit(X, y)
    slope = float(linreg.coef_[0])

    poly = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    poly.fit(X, y)

    future_X = np.arange(len(history), len(history) + forecast_days).reshape(-1, 1)
    forecast_linear = linreg.predict(future_X)
    forecast_poly = poly.predict(future_X)

    today = date.today()
    forecast = []
    for i in range(forecast_days):
        d = today + timedelta(days=i + 1)
        forecast.append({
            "date": d.isoformat(),
            "predicted_price_linear": round(float(forecast_linear[i]), 2),
            "predicted_price_poly": round(float(forecast_poly[i]), 2),
        })

    current_price = history[-1]["price"]
    projected_7d = forecast[-1]["predicted_price_poly"] if forecast else current_price
    pct_change = round(((projected_7d - current_price) / current_price) * 100, 2)

    direction = "rising" if slope > 0.02 else ("falling" if slope < -0.02 else "flat")

    return {
        "crop": crop,
        "unit": CROPS[crop]["unit"],
        "currency": CROPS[crop]["currency"],
        "history": history,
        "forecast": forecast,
        "trend_slope_per_day": round(slope, 4),
        "trend_direction": direction,
        "current_price": current_price,
        "projected_price_in_7_days": projected_7d,
        "projected_pct_change_7d": pct_change,
        "shelf_life_days": CROPS[crop]["shelf_life_days"],
    }


def list_crops() -> List[str]:
    return list(CROPS.keys())
