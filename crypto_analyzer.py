import asyncio
from datetime import datetime
from typing import Dict, Any
from layers.perception import PerceptionLayer
from layers.decision import DecisionLayer
from layers.memory import MemoryLayer
from models.analysis import Analysis
from models.preferences import UserPreferences

class CryptoAnalyzer:
    def __init__(self):
        self.perception = PerceptionLayer()
        self.decision = DecisionLayer()
        self.memory = MemoryLayer()

    async def analyze(self, symbol: str, preferences: UserPreferences) -> Analysis:
        print(f"\n=== Starting Enhanced Analysis for {symbol} ===")
        
        try:
            # Perception Phase with Market Context
            print("Gathering market data and context...")
            perceived_data = await self.perception.perceive(symbol, preferences)
            print(f"Market trend identified: {perceived_data['market_context']['trend']}")
            
            # Memory Integration
            print("Checking historical patterns...")
            historical_data = await self.memory.retrieve(f"{symbol}_historical", preferences.investment_horizon)
            if historical_data:
                print("Historical data found and integrated")
            
            # Enhanced Decision Making
            print("Processing decision with AI analysis...")
            decision = await self.decision.make_decision(
                perceived_data['technical_analysis'],
                preferences,
                historical_data
            )
            
            # Create comprehensive analysis
            analysis = Analysis(
                symbol=symbol,
                timestamp=datetime.now(),
                technical_analysis=perceived_data['technical_analysis'],
                market_data=perceived_data['market_data'],
                decision=decision,
                memory_context=historical_data
            )
            
            # Store analysis in memory
            await self.memory.store(
                f"{symbol}_historical",
                analysis.dict(),
                preferences.investment_horizon
            )
            
            # Output detailed analysis
            self._print_analysis_summary(analysis, perceived_data['market_context'])
            
            return analysis
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

    def _print_analysis_summary(self, analysis: Analysis, market_context: Dict[str, Any]):
        print("\n=== Analysis Summary ===")
        print(f"Symbol: {analysis.symbol}")
        print(f"Market Trend: {market_context['trend']}")
        print(f"Volume Profile: {market_context['volume_profile']}")
        print(f"\nTechnical Indicators:")
        print(f"RSI: {analysis.technical_analysis.rsi:.2f}")
        print(f"MACD: {analysis.technical_analysis.macd:.2f}")
        print(f"SMA 20: {analysis.technical_analysis.sma_20:.2f}")
        print(f"\nDecision:")
        print(f"Action: {analysis.decision.action}")
        print(f"Confidence: {analysis.decision.confidence:.2%}")
        print(f"Risk Score: {analysis.decision.risk_score:.2%}")
        print(f"Reasoning: {analysis.decision.reasoning}")