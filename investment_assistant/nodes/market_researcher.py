import yfinance as yf
import pandas as pd
from typing import Dict, Any
from datetime import datetime, timedelta
from ..analytics.technical_indicators import *
from ..analytics.fundamental_ratios import calculate_financial_ratios, calculate_financial_health_score
from ..config import get_llm
from langchain.prompts import ChatPromptTemplate

MARKET_ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
You are a senior equity research analyst. Analyze the following stock data and provide investment insights.

Stock: {symbol}
Current Price: ${current_price:.2f}
Price Change: {price_change_pct:+.2f}%

Technical Analysis:
- RSI (14-day): {rsi_value:.1f} ({rsi_signal})
- MACD: {macd_signal}
- Volatility (30-day): {volatility:.1f}%

Fundamental Analysis:
- P/E Ratio: {pe_ratio:.1f}
- ROE: {roe:.1%}
- Debt/Equity: {debt_equity:.2f}
- Financial Health Score: {health_score:.0f}/100 ({health_rating})

Market Context: {market_context}

Based on this analysis, provide:
1. A comprehensive investment thesis (2-3 sentences)
2. Key risks and opportunities (bullet points)
3. Clear recommendation: BUY/HOLD/SELL with confidence level (0-100%)

Format your response as:
THESIS: [investment thesis]
RISKS: [key risks]
OPPORTUNITIES: [key opportunities]  
RECOMMENDATION: [BUY/HOLD/SELL]
CONFIDENCE: [0-100]%
""")

def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetch comprehensive stock data"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, auto_adjust=True)
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def analyze_stock_technical(data: pd.DataFrame) -> Dict[str, Any]:
    """Perform technical analysis on stock data"""
    if data.empty:
        return {}
    
    close_prices = data['Close']
    
    # Calculate technical indicators
    rsi = calculate_rsi(close_prices)
    macd_data = calculate_macd(close_prices)
    volatility = calculate_volatility(close_prices)
    
    # Get latest values
    latest_rsi = rsi.iloc[-1] if not rsi.empty else 50
    rsi_signal = interpret_rsi(latest_rsi)
    macd_signal = interpret_macd(macd_data)
    
    return {
        'rsi_value': latest_rsi,
        'rsi_signal': rsi_signal,
        'macd_signal': macd_signal,
        'volatility': volatility * 100,  # Convert to percentage
        'current_price': close_prices.iloc[-1],
        'price_change_pct': ((close_prices.iloc[-1] / close_prices.iloc[-2]) - 1) * 100
    }

def get_market_context() -> str:
    """Get broader market context using S&P 500"""
    try:
        spy = yf.Ticker("SPY")
        spy_data = spy.history(period="1mo")
        spy_change = ((spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[0]) - 1) * 100
        
        if spy_change > 2:
            return f"Market is up {spy_change:.1f}% this month (bullish sentiment)"
        elif spy_change < -2:
            return f"Market is down {spy_change:.1f}% this month (bearish sentiment)"
        else:
            return f"Market is relatively flat this month ({spy_change:+.1f}%)"
    except:
        return "Market context unavailable"

def market_researcher_node(state: Dict) -> Dict:
    """Comprehensive market research analysis"""
    
    # Extract stock symbol from user message
    user_message = state.get("user_message", "")
    symbol = extract_stock_symbol(user_message)
    
    if not symbol:
        return {
            "market_analysis": "Could not identify a valid stock symbol in your request. Please specify a stock ticker (e.g., AAPL, TSLA, MSFT).",
            "recommendation": "HOLD",
            "confidence_score": 0.0
        }
    
    # Get stock data and perform analysis
    stock_data = get_stock_data(symbol)
    if stock_data.empty:
        return {
            "stock_symbol": symbol,
            "market_analysis": f"Unable to fetch data for {symbol}. Please verify the ticker symbol.",
            "recommendation": "HOLD", 
            "confidence_score": 0.0
        }
    
    # Technical analysis
    technical_analysis = analyze_stock_technical(stock_data)
    
    # Fundamental analysis
    fundamental_ratios = calculate_financial_ratios(symbol)
    health_score, health_rating = calculate_financial_health_score(fundamental_ratios)
    
    # Market context
    market_context = get_market_context()
    
    # Generate AI analysis
    llm = get_llm()
    chain = MARKET_ANALYSIS_PROMPT | llm
    
    analysis_result = chain.invoke({
        "symbol": symbol,
        "current_price": technical_analysis.get('current_price', 0),
        "price_change_pct": technical_analysis.get('price_change_pct', 0),
        "rsi_value": technical_analysis.get('rsi_value', 50),
        "rsi_signal": technical_analysis.get('rsi_signal', 'neutral'),
        "macd_signal": technical_analysis.get('macd_signal', 'neutral'),
        "volatility": technical_analysis.get('volatility', 0),
        "pe_ratio": fundamental_ratios.get('PE_Ratio', 0),
        "roe": fundamental_ratios.get('ROE', 0),
        "debt_equity": fundamental_ratios.get('Debt_To_Equity', 0),
        "health_score": health_score,
        "health_rating": health_rating,
        "market_context": market_context
    })
    
    # Parse AI response
    content = analysis_result.content
    recommendation, confidence = parse_recommendation(content)
    
    return {
        "stock_symbol": symbol,
        "current_price": technical_analysis.get('current_price', 0),
        "price_change_pct": technical_analysis.get('price_change_pct', 0),
        "technical_signals": {
            "RSI": technical_analysis.get('rsi_signal', 'neutral'),
            "MACD": technical_analysis.get('macd_signal', 'neutral')
        },
        "fundamental_ratios": fundamental_ratios,
        "market_analysis": content,
        "recommendation": recommendation,
        "confidence_score": confidence
    }

def extract_stock_symbol(text: str) -> str:
    """Extract stock symbol from user message"""
    import re
    
    # Look for common patterns
    patterns = [
        r'\b([A-Z]{1,5})\b',  # All caps words 1-5 characters
        r'ticker[:\s]+([A-Z]+)',  # "ticker: AAPL"
        r'stock[:\s]+([A-Z]+)',   # "stock: AAPL"
    ]
    
    # Common stock names to symbols mapping
    symbol_mapping = {
        'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL',
        'amazon': 'AMZN', 'tesla': 'TSLA', 'facebook': 'META',
        'netflix': 'NFLX', 'nvidia': 'NVDA', 'amd': 'AMD'
    }
    
    text_lower = text.lower()
    
    # Check for company names first
    for name, symbol in symbol_mapping.items():
        if name in text_lower:
            return symbol
    
    # Then look for ticker patterns
    for pattern in patterns:
        matches = re.findall(pattern, text.upper())
        if matches:
            potential_symbol = matches[0]
            # Validate it's a reasonable stock symbol length
            if 1 <= len(potential_symbol) <= 5:
                return potential_symbol
    
    return ""

def parse_recommendation(content: str) -> tuple:
    """Parse recommendation and confidence from AI response"""
    import re
    
    # Extract recommendation
    rec_pattern = r'RECOMMENDATION:\s*(BUY|SELL|HOLD)'
    rec_match = re.search(rec_pattern, content)
    recommendation = rec_match.group(1) if rec_match else "HOLD"
    
    # Extract confidence
    conf_pattern = r'CONFIDENCE:\s*(\d+)%'
    conf_match = re.search(conf_pattern, content)
    confidence = float(conf_match.group(1)) / 100 if conf_match else 0.5
    
    return recommendation, confidence
