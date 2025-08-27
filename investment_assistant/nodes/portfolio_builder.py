from typing import Dict, List, Any
from datetime import date
import yfinance as yf
from ..config import get_llm

def _age_from_range(age_range: str) -> int:
    """Convert age range to numeric value for calculations"""
    mapping = {"young": 30, "middle-aged": 45, "senior": 65}
    return mapping.get(age_range, 40)

def _risk_shift(risk: str) -> float:
    """Get risk tolerance adjustment factor"""
    return {"aggressive": +0.10, "moderate": 0.0, "conservative": -0.10}.get(risk, 0.0)

def _equity_allocation(age: int, risk: str) -> float:
    """Calculate equity allocation using 110-age rule with risk adjustment"""
    base = max(0.1, min(0.9, (110 - age) / 100.0))  # rule of 110-age
    return min(0.9, max(0.1, base + _risk_shift(risk)))

def _select_etfs(equity_pct: float, bond_pct: float) -> List[Dict[str, Any]]:
    """Select and weight ETFs based on allocation"""
    etfs = [
        ("SPY", equity_pct * 0.60),    # US Large Cap
        ("IEFA", equity_pct * 0.20),   # International Developed
        ("VWO", equity_pct * 0.20),    # Emerging Markets
        ("AGG", bond_pct * 0.70),      # Aggregate Bonds
        ("SHY", bond_pct * 0.30),      # Short-term Treasury
    ]
    
    # Fetch latest prices (suppress warnings)
    try:
        tickers = [t for t, _ in etfs if _ > 0.01]  # Only fetch if meaningful weight
        if tickers:
            prices = yf.download(
                tickers, 
                period="1d", 
                progress=False, 
                auto_adjust=True,  # Suppress FutureWarning
                show_errors=False
            )["Close"].iloc[-1]
        else:
            prices = {}
    except Exception:
        prices = {}  # Fallback if yfinance fails
    
    return [
        {
            "ticker": t, 
            "weight": round(w, 4), 
            "price": float(prices.get(t, 0.0)) if t in prices else 0.0
        }
        for t, w in etfs if w > 0.01
    ]

def portfolio_builder_node(state: Dict) -> Dict:
    """Build portfolio allocation and ETF selection based on user profile"""
    
    # Extract profile information
    age = _age_from_range(state.get("age_range", "middle-aged"))
    risk = state.get("risk_tolerance", "moderate")
    horizon = state.get("investment_horizon", "medium")
    
    # Calculate allocation
    equity_pct = _equity_allocation(age, risk)
    bond_pct = 1.0 - equity_pct
    
    # Create allocation dictionary
    allocation = {
        "equity": round(equity_pct, 3),
        "bonds": round(bond_pct, 3)
    }
    
    # Select ETFs
    etfs = _select_etfs(equity_pct, bond_pct)
    
    # Generate reasoning
    reasoning = (
        f"Applied the 110-age rule for a {risk} risk investor aged ~{age} "
        f"with {horizon}-term horizon. "
        f"Target allocation: {allocation['equity']*100:.0f}% equity / "
        f"{allocation['bonds']*100:.0f}% bonds, implemented via "
        f"{len(etfs)} diversified low-cost ETFs."
    )
    
    return {
        "recommended_allocation": allocation,
        "etf_selection": etfs,
        "builder_reasoning": reasoning
    }
