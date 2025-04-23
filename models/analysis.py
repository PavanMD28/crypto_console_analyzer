from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class Decision(BaseModel):
    action: str
    confidence: float
    risk_score: float
    reasoning: str
    timestamp: datetime

class MarketData(BaseModel):
    prices: List[float]
    volumes: List[float]
    dates: List[datetime]

class TechnicalIndicators(BaseModel):
    rsi: float
    macd: float
    sma_20: float
    volume_trend: float

class Analysis(BaseModel):
    symbol: str
    timestamp: datetime
    technical_analysis: TechnicalIndicators
    market_data: MarketData
    decision: Decision
    memory_context: Optional[Dict] = None