import google.generativeai as genai
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from config import configure_gemini
from models.analysis import Decision, TechnicalIndicators
from models.preferences import UserPreferences
from layers.prompts import AnalysisPrompts
# MCP imports
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys

class PerceptionLayer:
    def __init__(self):
        self.prompts = AnalysisPrompts()
        self.model = configure_gemini()
        self.mcp = FastMCP("PerceptionLayer")
        self.model_config = {
            'temperature': 0.1,
            'candidate_count': 1,
            'max_output_tokens': 512
        }
        self.register_tools()  # Register tools during initialization

    def calculate_risk_adjusted_return(self, returns: List[float], risk_free_rate: float) -> float:
        """Calculate the risk-adjusted return using MCP"""
        print("CALLED: calculate_risk_adjusted_return(returns: List[float], risk_free_rate: float) -> float:")
        excess_returns = [r - risk_free_rate for r in returns]
        return sum(excess_returns) / len(excess_returns)

    def register_tools(self):
        # Register the tool with MCP
        self.mcp.tool()(self.calculate_risk_adjusted_return)

class DecisionLayer:
    def __init__(self):
        self.prompts = AnalysisPrompts()
        self.model = configure_gemini()
        self.mcp = FastMCP("DecisionLayer")
        self.model_config = {
            'temperature': 0.1,
            'candidate_count': 1,
            'max_output_tokens': 512
        }
        self.register_tools()  # Register tools during initialization

    def _calculate_confidence(self, technical: TechnicalIndicators, preferred_indicators: List[str]) -> float:
        """Calculate confidence based on technical indicators and user preferences."""
        confidence_scores = {
            'RSI': self._get_rsi_confidence(technical.rsi),
            'MACD': self._get_macd_confidence(technical.macd),
            'SMA': self._get_sma_confidence(technical.sma_20),
            'VOLUME': self._get_volume_confidence(technical.volume_trend)
        }
        
        total_score = 0
        valid_indicators = 0
        
        for indicator in preferred_indicators:
            if indicator in confidence_scores:
                total_score += confidence_scores[indicator]
                valid_indicators += 1
        
        return total_score / max(valid_indicators, 1)

    # Define the helper methods for confidence calculation
    def _get_rsi_confidence(self, rsi: float) -> float:
        if rsi > 70 or rsi < 30:
            return 0.9  # Strong signal
        elif rsi > 60 or rsi < 40:
            return 0.7  # Moderate signal
        return 0.5  # Weak signal

    def _get_macd_confidence(self, macd: float) -> float:
        return min(0.9, abs(macd) / 2) if macd != 0 else 0.5

    def _get_sma_confidence(self, sma: float) -> float:
        return 0.7  # Base confidence for trend following

    def _get_volume_confidence(self, volume_trend: float) -> float:
        return min(0.9, abs(volume_trend) + 0.5)

    def calculate_risk_adjusted_return(self, returns: List[float], risk_free_rate: float) -> float:
        """Calculate the risk-adjusted return using MCP"""
        print("CALLED: calculate_risk_adjusted_return(returns: List[float], risk_free_rate: float) -> float:")
        excess_returns = [r - risk_free_rate for r in returns]
        return sum(excess_returns) / len(excess_returns)

    def register_tools(self):
        # Register the tool with MCP
        self.mcp.tool()(self.calculate_risk_adjusted_return)

    async def make_decision(self, technical: TechnicalIndicators, preferences: UserPreferences, historical_data: Optional[Dict] = None) -> Decision:
        # Use MCP tool to calculate risk-adjusted return
        if historical_data:
            risk_adjusted_return = self.calculate_risk_adjusted_return(historical_data['returns'], historical_data['risk_free_rate'])
            print(f"Risk-adjusted return: {risk_adjusted_return}")
        # Get risk assessment with optimized prompt
        risk_prompt = self.prompts.get_risk_assessment_prompt(technical, preferences)
        risk_assessment = await self._process_prompt(risk_prompt)
        risk_score = self._extract_risk_score(risk_assessment)
        
        # Calculate confidence
        confidence = self._calculate_confidence(technical, preferences.preferred_indicators)
        
        # Get action recommendation with optimized prompt
        action_prompt = self.prompts.get_action_recommendation_prompt(risk_score, confidence, preferences)
        action_recommendation = await self._process_prompt(action_prompt)
        action, reasoning = self._extract_action_and_reasoning(action_recommendation)
        
        # Validate decision with optimized prompt
        validation_prompt = self.prompts.get_validation_prompt(action, confidence)
        validation_result = await self._process_prompt(validation_prompt)
        
        return self._finalize_decision(action, risk_score, confidence, reasoning, validation_result, preferences)

    def _extract_action_and_reasoning(self, recommendation: str) -> Tuple[str, str]:
        action = 'HOLD'
        reasoning = 'Insufficient data for analysis'
        
        if not recommendation:
            return action, reasoning
            
        lines = recommendation.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ACTION:'):
                extracted_action = line.split(':')[1].strip('[] ').upper()
                if extracted_action in ['BUY', 'SELL', 'HOLD']:
                    action = extracted_action
            elif line.startswith('REASON:') or line.startswith('SUPPORT:'):
                extracted_reason = line.split(':')[1].strip('[] ')
                if extracted_reason:
                    reasoning = extracted_reason
            elif line.startswith('MITIGATION:'):
                mitigation = line.split(':')[1].strip('[] ')
                if mitigation:
                    reasoning += f" Risk mitigation: {mitigation}"
                
        return action, reasoning

    def _extract_risk_score(self, risk_assessment: str) -> float:
        if not risk_assessment:
            return 0.5
            
        risk_levels = {'LOW': 0.3, 'MEDIUM': 0.5, 'HIGH': 0.7}
        for line in risk_assessment.split('\n'):
            if line.startswith('RISK:'):
                level = line.split(':')[1].strip('[] ').upper()
                if level in risk_levels:
                    return risk_levels[level]
        return 0.5

    def _finalize_decision(self, action: str, risk: float, confidence: float, 
                         reasoning: str, validation: str, preferences: UserPreferences) -> Decision:
        return Decision(
            action=action,
            confidence=confidence,
            risk_score=risk,
            reasoning=reasoning,
            timestamp=datetime.now()
        )

    async def _process_prompt(self, prompt: str) -> str:
        """Process a prompt using the configured model."""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.model_config
            )
            return response.text if response else ""
        except Exception as e:
            print(f"Error processing prompt with Flash model: {str(e)}")