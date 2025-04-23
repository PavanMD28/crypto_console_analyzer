# Crypto Console Analyzer

## Overview
Crypto Console Analyzer is a sophisticated tool designed to analyze cryptocurrency markets using advanced AI models. It provides insights into market trends, risk assessments, and trade recommendations based on user preferences and technical indicators.

## Features
- **Market Analysis**: Gather and analyze market data to identify trends and patterns.
- **Risk Assessment**: Evaluate market risks using technical indicators and user-defined preferences.
- **Trade Recommendations**: Generate actionable trade recommendations with reasoning and support.
- **Historical Analysis**: View historical data and patterns for informed decision-making.

## Configuration
User preferences can be configured to tailor the analysis to specific needs. Preferences include risk tolerance, preferred indicators, investment horizon, and notification frequency.

## Key Files and Layers
- main.py : The entry point for running the console application.
- layers/prompts.py : Contains the AnalysisPrompts class for generating prompts used in analysis.
- layers/decision.py : Implements decision-making logic using MCP tools.
- layers/perception.py : Handles perception-related tasks and integrates with MCP.
- models/preferences.py : Defines the UserPreferences class for managing user preferences.
## Technical Indicators
The analyzer uses various technical indicators such as RSI, MACD, SMA, and Volume to assess market conditions and generate recommendations.

## MCP Integration
The project utilizes MCP (Multi-Modal Content Processing) for enhanced analysis capabilities. MCP tools are registered and used within the decision-making layer to process and analyze data effectively.

## Pydantic Usage
pydantic is used for data validation and management of technical indicators. The TechnicalIndicators model ensures that the data passed to the prompts is correctly structured and validated.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

## Installation
To install and set up the Crypto Console Analyzer, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto_console_analyzer.git
