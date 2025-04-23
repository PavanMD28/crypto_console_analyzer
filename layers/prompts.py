from typing import Dict, Any
from pydantic import BaseModel
from models.preferences import UserPreferences
from config import configure_gemini

class TechnicalIndicators(BaseModel):
    rsi: float
    macd: float
    sma_20: float
    volume_trend: float

class AnalysisPrompts:
    def __init__(self):
        self.model = configure_gemini()
        self.prompt_rules = {
            "explicit_reasoning": True,
            "structured_output": True,
            "tool_separation": True,
            "conversation_loop": True,
            "instructional_framing": True
        }

    async def _process_prompt(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text if response else ""
        except Exception as e:
            print(f"Error processing prompt: {str(e)}")
            return ""

    def get_risk_assessment_prompt(self, technical: TechnicalIndicators, preferences: UserPreferences) -> str:
        return f"""Analyze crypto market risk:
Technical: {self._format_indicators(technical)}
Risk Tolerance: {preferences.risk_tolerance}
Horizon: {preferences.investment_horizon}
Output:
RISK:[LOW/MEDIUM/HIGH]
EVIDENCE:[key factors]
CONFIDENCE:[0-1]"""

    def get_action_recommendation_prompt(self, risk_score: float, confidence: float, preferences: UserPreferences) -> str:
        return f"""Recommend crypto trade action:
Risk:{risk_score:.2f}
Confidence:{confidence:.2f}
Tolerance:{preferences.risk_tolerance}
Horizon:{preferences.investment_horizon}
Indicators:{','.join(preferences.preferred_indicators)}
Output:
ACTION:[BUY/SELL/HOLD]
REASON:[main factor]
SUPPORT:[considerations]
MITIGATION:[measures]"""

    def get_market_context_prompt(self, symbol: str, timeframe: str) -> str:
        return f"""Analyze {symbol} market context:
Timeframe:{timeframe}
Output:
TREND:[UP/DOWN/SIDEWAYS]
VOLUME:[INCREASING/DECREASING/STABLE]
SUPPORT:[levels]
RESISTANCE:[levels]
PATTERNS:[formations]"""

    def _format_indicators(self, technical) -> str:
        return f"RSI:{technical.rsi:.2f},MACD:{technical.macd:.2f},SMA20:{technical.sma_20:.2f},VOL:{technical.volume_trend:.2f}"

    def get_validation_prompt(self, decision: str, confidence: float) -> str:
        return f"""Valida
        te crypto decision:
Action:{decision}
Confidence:{confidence:.2f}
Output:
QUALITY:[pass/fail]
LOGIC:[valid/invalid]
RISK:[acceptable/high]
ALTERNATIVES:[options]"""