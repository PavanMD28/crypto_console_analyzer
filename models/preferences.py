from pydantic import BaseModel
from typing import List

class UserPreferences(BaseModel):
    risk_tolerance: str = "medium"  # low, medium, high
    preferred_indicators: List[str] = ["RSI", "MACD", "SMA"]
    investment_horizon: str = "medium"  # short, medium, long
    max_risk_percentage: float = 0.7
    notification_frequency: str = "real-time"  # real-time, daily, weekly