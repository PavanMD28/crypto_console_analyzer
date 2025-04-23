import asyncio
from crypto_analyzer import CryptoAnalyzer
from models.preferences import UserPreferences

async def run_analysis(analyzer: CryptoAnalyzer, symbol: str, preferences: UserPreferences):
    try:
        analysis = await analyzer.analyze(symbol, preferences)
        return analysis
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        return None

async def main():
    analyzer = CryptoAnalyzer()
    
    # Initialize default preferences at the start
    preferences = get_user_preferences()
    print("\nDefault preferences configured!")
    
    while True:
        print("\n=== Crypto Analyzer Console ===")
        print("1. Configure Preferences")
        print("2. Analyze BTC")
        print("3. Analyze ETH")
        print("4. Analyze Custom Token")
        print("5. View Historical Analysis")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '6':
            break
            
        if choice == '1':
            preferences = get_user_preferences()
            print("\nPreferences updated successfully!")
            continue
            
        if choice == '5':
            symbol = input("Enter token symbol to view history: ")
            # Historical analysis view will be handled here
            continue
            
        symbol = {
            '2': 'BTC',
            '3': 'ETH',
            '4': input("Enter token symbol (e.g., BTC, ETH): ")
        }.get(choice)
        
        if symbol:
            print(f"\nStarting analysis for {symbol}...")
            analysis = await run_analysis(analyzer, symbol, preferences)
            
            if analysis:
                input("\nPress Enter to continue...")

def get_user_preferences() -> UserPreferences:
    print("\n=== Configure Analysis Preferences ===")
    
    risk_tolerance = input("Risk tolerance (low/medium/high) [medium]: ").lower() or "medium"
    
    print("\nSelect preferred indicators (comma-separated):")
    print("Available: RSI, MACD, SMA, Volume, Bollinger")
    indicators = input("[RSI,MACD,SMA]: ").upper().split(",") or ["RSI", "MACD", "SMA"]
    
    horizon = input("Investment horizon (short/medium/long) [medium]: ").lower() or "medium"
    
    try:
        risk_percentage = float(input("Maximum risk percentage (0-1) [0.7]: ") or 0.7)
    except ValueError:
        risk_percentage = 0.7

    notifications = input("Notification frequency (real-time/daily/weekly) [real-time]: ").lower() or "real-time"

    return UserPreferences(
        risk_tolerance=risk_tolerance,
        preferred_indicators=indicators,
        investment_horizon=horizon,
        max_risk_percentage=risk_percentage,
        notification_frequency=notifications
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        print("Analysis session ended.")