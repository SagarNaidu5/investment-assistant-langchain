import yfinance as yf
from typing import Dict, Optional, Tuple
import pandas as pd

def calculate_financial_ratios(ticker: str) -> Dict[str, float]:
    """Calculate key fundamental ratios using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        ratios = {}
        
        # Valuation Ratios
        ratios['PE_Ratio'] = info.get('forwardPE', info.get('trailingPE', 0))
        ratios['PB_Ratio'] = info.get('priceToBook', 0)
        ratios['PS_Ratio'] = info.get('priceToSalesTrailing12Months', 0)
        
        # Profitability Ratios
        ratios['ROE'] = info.get('returnOnEquity', 0)
        ratios['ROA'] = info.get('returnOnAssets', 0)
        ratios['Profit_Margin'] = info.get('profitMargins', 0)
        ratios['Operating_Margin'] = info.get('operatingMargins', 0)
        
        # Financial Health Ratios
        ratios['Current_Ratio'] = info.get('currentRatio', 0)
        ratios['Debt_To_Equity'] = info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0
        ratios['Interest_Coverage'] = calculate_interest_coverage(financials)
        
        # Growth Ratios
        ratios['Revenue_Growth'] = info.get('revenueGrowth', 0)
        ratios['Earnings_Growth'] = info.get('earningsGrowth', 0)
        
        return ratios
    except Exception as e:
        print(f"Error calculating ratios for {ticker}: {e}")
        return {}

def calculate_interest_coverage(financials: pd.DataFrame) -> float:
    """Calculate interest coverage ratio from financials"""
    try:
        if financials.empty:
            return 0
        
        ebit = financials.loc['Operating Income'].iloc[0] if 'Operating Income' in financials.index else 0
        interest_expense = abs(financials.loc['Interest Expense'].iloc[0]) if 'Interest Expense' in financials.index else 1
        
        return ebit / interest_expense if interest_expense > 0 else 0
    except:
        return 0

def calculate_financial_health_score(ratios: Dict[str, float]) -> Tuple[float, str]:
    """Calculate overall financial health score (0-100)"""
    score = 0
    max_score = 100
    
    # Profitability (30 points)
    if ratios.get('ROE', 0) > 0.15:
        score += 10
    elif ratios.get('ROE', 0) > 0.10:
        score += 7
    elif ratios.get('ROE', 0) > 0.05:
        score += 4
        
    if ratios.get('Profit_Margin', 0) > 0.20:
        score += 10
    elif ratios.get('Profit_Margin', 0) > 0.10:
        score += 7
    elif ratios.get('Profit_Margin', 0) > 0.05:
        score += 4
        
    if ratios.get('Operating_Margin', 0) > 0.15:
        score += 10
    elif ratios.get('Operating_Margin', 0) > 0.10:
        score += 7
    elif ratios.get('Operating_Margin', 0) > 0.05:
        score += 4
    
    # Valuation (25 points)
    pe_ratio = ratios.get('PE_Ratio', 0)
    if 0 < pe_ratio < 15:
        score += 15
    elif 15 <= pe_ratio < 25:
        score += 10
    elif 25 <= pe_ratio < 35:
        score += 5
        
    pb_ratio = ratios.get('PB_Ratio', 0)
    if 0 < pb_ratio < 1.5:
        score += 10
    elif 1.5 <= pb_ratio < 3:
        score += 7
    elif 3 <= pb_ratio < 5:
        score += 4
    
    # Financial Health (25 points)
    current_ratio = ratios.get('Current_Ratio', 0)
    if current_ratio > 2:
        score += 10
    elif current_ratio > 1.5:
        score += 7
    elif current_ratio > 1:
        score += 4
        
    debt_to_equity = ratios.get('Debt_To_Equity', 0)
    if debt_to_equity < 0.3:
        score += 10
    elif debt_to_equity < 0.6:
        score += 7
    elif debt_to_equity < 1:
        score += 4
        
    if ratios.get('Interest_Coverage', 0) > 5:
        score += 5
    elif ratios.get('Interest_Coverage', 0) > 2:
        score += 3
    
    # Growth (20 points)
    if ratios.get('Revenue_Growth', 0) > 0.15:
        score += 10
    elif ratios.get('Revenue_Growth', 0) > 0.05:
        score += 7
    elif ratios.get('Revenue_Growth', 0) > 0:
        score += 4
        
    if ratios.get('Earnings_Growth', 0) > 0.15:
        score += 10
    elif ratios.get('Earnings_Growth', 0) > 0.05:
        score += 7
    elif ratios.get('Earnings_Growth', 0) > 0:
        score += 4
    
    # Determine rating
    if score >= 80:
        rating = "Excellent"
    elif score >= 65:
        rating = "Good"
    elif score >= 50:
        rating = "Average"
    elif score >= 35:
        rating = "Below Average"
    else:
        rating = "Poor"
    
    return score, rating
