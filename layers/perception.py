from typing import Dict, Any, List
import yfinance as yf
import pandas as pd
from config import configure_gemini
from models.analysis import MarketData, TechnicalIndicators
from models.preferences import UserPreferences
from layers.prompts import AnalysisPrompts
from mcp.server.fastmcp import FastMCP  # Assuming FastMCP is the correct client

class PerceptionLayer:
    def __init__(self):
        self.prompts = AnalysisPrompts()
        self.model = configure_gemini()
        self.mcp_client = FastMCP("PerceptionLayer")  # Initialize with FastMCP

    async def _process_prompt(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'candidate_count': 1,
                    'max_output_tokens': 512
                }
            )
            return response.text if response else ""
        except Exception as e:
            print(f"Error processing prompt with Flash model: {str(e)}")
            return ""

    def _fetch_market_data(self, symbol: str, horizon: str) -> pd.DataFrame:
        periods = {
            'short': '180d',  # Increased from 90d to 180d
            'medium': '365d',  # Increased from 180d to 365d
            'long': '730d'  # Increased from 365d to 730d (2 years)
        }
        ticker = yf.Ticker(f"{symbol}-USD")
        return ticker.history(period=periods.get(horizon, '365d'))  # Default to medium if not specified

    async def perceive(self, symbol: str, preferences: UserPreferences) -> Dict[str, Any]:
        # Allow more tokens for analysis
        supported_tokens = ['BTC', 'ETH', 'SOL', 'DOT', 'ADA', 'XRP', 'LTC', 'BCH']
        if symbol not in supported_tokens:
            raise ValueError(f"Unsupported token: {symbol}. Supported tokens are: {', '.join(supported_tokens)}")
        
        market_data = self._fetch_market_data(symbol, preferences.investment_horizon)
        technical = self._calculate_technical_indicators(market_data)
        
        # Use MCP server for additional processing
        mcp_result = self.mcp_client.process_data(market_data)
        
        context_prompt = self.prompts.get_market_context_prompt(symbol, preferences.investment_horizon)
        market_context = await self._process_prompt(context_prompt)
        
        return {
            'market_data': self._format_market_data(market_data),
            'technical_analysis': technical,
            'mcp_result': mcp_result,  # Include MCP result in the output
            'market_context': self._parse_market_context(market_context)
        }

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> TechnicalIndicators:
        return TechnicalIndicators(
            rsi=self._calculate_rsi(data['Close']),
            macd=self._calculate_macd(data['Close']),
            sma_20=self._calculate_sma(data['Close'], 20),
            volume_trend=self._calculate_volume_trend(data['Volume'])
        )

    async def _process_prompt(self, prompt: str) -> str:
        try:
            # Using Flash model for faster inference
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.model_config,
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_DANGEROUS",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            
            # Flash model specific response handling
            if hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.text
            return response.text
            
        except Exception as e:
            print(f"Error processing prompt with Flash model: {str(e)}")
            return ""

    async def perceive(self, symbol: str, preferences: UserPreferences) -> Dict[str, Any]:
        market_data = self._fetch_market_data(symbol, preferences.investment_horizon)
        technical = self._calculate_technical_indicators(market_data)
        
        context_prompt = self.prompts.get_market_context_prompt(symbol, preferences.investment_horizon)
        market_context = await self._process_prompt(context_prompt)
        
        return {
            'market_data': self._format_market_data(market_data),
            'technical_analysis': technical,
            'market_context': self._parse_market_context(market_context)
        }

    def _parse_market_context(self, context: str) -> Dict[str, Any]:
        parsed = {
            'trend': 'SIDEWAYS',
            'volume_profile': 'STABLE',
            'support_levels': [],
            'resistance_levels': [],
            'patterns': []
        }
        
        for line in context.split('\n'):
            if line.startswith('TREND:'):
                parsed['trend'] = line.split(':')[1].strip('[]')
            elif line.startswith('VOLUME:'):
                parsed['volume_profile'] = line.split(':')[1].strip('[]')
            elif line.startswith('SUPPORT:'):
                parsed['support_levels'] = [float(x) for x in line.split(':')[1].strip('[]').split(',') if x.strip()]
            elif line.startswith('RESISTANCE:'):
                parsed['resistance_levels'] = [float(x) for x in line.split(':')[1].strip('[]').split(',') if x.strip()]
            elif line.startswith('PATTERNS:'):
                parsed['patterns'] = [x.strip() for x in line.split(':')[1].strip('[]').split(',') if x.strip()]
        
        return parsed

    def _format_market_data(self, data: pd.DataFrame) -> MarketData:
        return MarketData(
            prices=data['Close'].tolist(),
            volumes=data['Volume'].tolist(),
            dates=data.index.tolist()
        )

    def _calculate_rsi(self, prices, periods=14):
        import numpy as np
        
        deltas = np.diff(prices)
        seed = deltas[:periods+1]
        up = deltas[:periods+1].sum()/periods
        down = -seed[seed < 0].sum()/periods
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:periods] = 100. - 100./(1. + rs)

        for i in range(periods, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(periods-1) + upval)/periods
            down = (down*(periods-1) + downval)/periods
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return rsi[-1]

    def _calculate_macd(self, prices, slow=26, fast=12, signal=9):
        import numpy as np
        
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd.iloc[-1] - signal_line.iloc[-1]

    def _calculate_sma(self, prices, window):
        return prices.rolling(window=window).mean().iloc[-1]

    def _calculate_volume_trend(self, volumes, window=20):
        avg_volume = volumes.rolling(window=window).mean()
        return (volumes.iloc[-1] / avg_volume.iloc[-1]) - 1