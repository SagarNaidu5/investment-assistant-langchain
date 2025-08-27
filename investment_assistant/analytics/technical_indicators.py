import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return {
        'MACD': macd_line,
        'Signal': signal_line,
        'Histogram': histogram
    }

def calculate_moving_averages(prices: pd.Series, windows: list = [20, 50, 200]) -> Dict[str, pd.Series]:
    """Calculate multiple moving averages"""
    return {f'MA_{window}': prices.rolling(window=window).mean() for window in windows}

def interpret_rsi(rsi_value: float) -> str:
    """Interpret RSI signals"""
    if rsi_value >= 70:
        return "overbought"
    elif rsi_value <= 30:
        return "oversold"
    elif rsi_value >= 60:
        return "strong"
    elif rsi_value <= 40:
        return "weak"
    else:
        return "neutral"

def interpret_macd(macd_data: Dict[str, pd.Series]) -> str:
    """Interpret MACD signals"""
    latest_macd = macd_data['MACD'].iloc[-1]
    latest_signal = macd_data['Signal'].iloc[-1]
    latest_histogram = macd_data['Histogram'].iloc[-1]
    
    if latest_macd > latest_signal and latest_histogram > 0:
        return "bullish"
    elif latest_macd < latest_signal and latest_histogram < 0:
        return "bearish"
    else:
        return "neutral"

def calculate_volatility(prices: pd.Series, window: int = 30) -> float:
    """Calculate price volatility"""
    returns = prices.pct_change().dropna()
    return returns.rolling(window=window).std().iloc[-1] * np.sqrt(252)
