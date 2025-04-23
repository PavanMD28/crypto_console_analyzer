import pandas as pd
import numpy as np
from typing import Dict

class TechnicalAnalysis:
    def analyze(self, data: pd.DataFrame) -> Dict:
        return {
            'rsi': self._calculate_rsi(data['Close']),
            'macd': self._calculate_macd(data['Close']),
            'sma_20': self._calculate_sma(data['Close'], 20),
            'volume_trend': self._calculate_volume_trend(data['Volume'])
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_macd(self, prices: pd.Series) -> float:
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        return macd.iloc[-1]

    def _calculate_sma(self, prices: pd.Series, period: int) -> float:
        return prices.rolling(window=period).mean().iloc[-1]

    def _calculate_volume_trend(self, volume: pd.Series) -> float:
        return (volume.iloc[-5:].mean() - volume.iloc[-10:-5].mean()) / volume.iloc[-10:-5].mean()