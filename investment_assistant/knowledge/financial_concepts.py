from typing import Dict, List
import json

class FinancialKnowledgeBase:
    """Comprehensive financial education knowledge base"""
    
    def __init__(self):
        self.knowledge_base = {
            # Basic Financial Concepts
            "compound_interest": {
                "definition": "The process where interest is earned on both the original principal and previously earned interest, creating exponential growth over time.",
                "key_points": [
                    "Einstein allegedly called it 'the eighth wonder of the world'",
                    "Time is the most important factor in compound growth",
                    "Small amounts invested early can outperform large amounts invested later"
                ],
                "example": "₹10,000 invested at 8% annual interest becomes ₹10,800 in year 1, ₹11,664 in year 2, ₹12,597 in year 3, growing exponentially.",
                "formula": "A = P(1 + r/n)^(nt) where P=principal, r=rate, n=compounding frequency, t=time",
                "related_concepts": ["time_value_of_money", "investing", "retirement_planning"]
            },
            
            "time_value_of_money": {
                "definition": "The concept that money available today is worth more than the same amount in the future due to its earning potential.",
                "key_points": [
                    "Money can be invested to generate returns over time",
                    "Inflation erodes purchasing power over time",
                    "Present value calculations help compare future cash flows"
                ],
                "example": "₹100 today at 10% interest is worth ₹110 in one year, making it more valuable than receiving ₹100 next year.",
                "applications": ["Investment valuation", "Loan calculations", "Retirement planning"],
                "related_concepts": ["compound_interest", "inflation", "present_value"]
            },
            
            "risk_return_relationship": {
                "definition": "The fundamental investment principle that higher potential returns typically come with higher levels of risk.",
                "key_points": [
                    "Risk and return are directly correlated in efficient markets",
                    "Diversification can reduce risk without proportionally reducing returns",
                    "Risk tolerance varies by individual circumstances and timeline"
                ],
                "risk_levels": {
                    "Low": "Government bonds, savings accounts (2-4% returns)",
                    "Medium": "Diversified mutual funds, blue-chip stocks (6-10% returns)",
                    "High": "Growth stocks, emerging markets (10%+ potential, higher volatility)"
                },
                "related_concepts": ["diversification", "asset_allocation", "volatility"]
            },
            
            "diversification": {
                "definition": "The strategy of spreading investments across different assets, sectors, or geographies to reduce overall portfolio risk.",
                "key_points": [
                    "Don't put all eggs in one basket",
                    "Reduces unsystematic (company-specific) risk",
                    "Can be achieved through asset classes, sectors, or geography"
                ],
                "types": [
                    "Asset Class: Stocks, bonds, real estate, commodities",
                    "Sector: Technology, healthcare, finance, consumer goods",
                    "Geographic: Domestic vs. international markets"
                ],
                "example": "A portfolio with 60% stocks, 30% bonds, 10% REITs is less risky than 100% in one stock.",
                "related_concepts": ["asset_allocation", "correlation", "modern_portfolio_theory"]
            },
            
            # Investment Vehicles
            "stocks": {
                "definition": "Shares of ownership in a company that entitle holders to a portion of profits and voting rights.",
                "key_points": [
                    "Represent ownership stake in companies",
                    "Can provide returns through dividends and capital appreciation",
                    "Higher risk but historically higher long-term returns than bonds"
                ],
                "types": {
                    "Common Stock": "Voting rights, variable dividends",
                    "Preferred Stock": "Fixed dividends, no voting rights, priority in liquidation"
                },
                "risks": ["Market volatility", "Company-specific risk", "Economic downturns"],
                "related_concepts": ["dividends", "capital_gains", "market_capitalization"]
            },
            
            "bonds": {
                "definition": "Debt securities where investors loan money to entities (government/corporate) in exchange for periodic interest payments plus return of principal.",
                "key_points": [
                    "Lower risk than stocks but also lower expected returns",
                    "Provide steady income through interest payments",
                    "Bond prices move inversely to interest rates"
                ],
                "types": {
                    "Government Bonds": "Issued by national governments, lowest risk",
                    "Corporate Bonds": "Issued by companies, higher yield but more risk",
                    "Municipal Bonds": "Issued by local governments, often tax-exempt"
                },
                "risks": ["Interest rate risk", "Credit risk", "Inflation risk"],
                "related_concepts": ["interest_rates", "credit_rating", "duration"]
            },
            
            "mutual_funds": {
                "definition": "Investment vehicles that pool money from many investors to purchase a diversified portfolio of stocks, bonds, or other securities.",
                "key_points": [
                    "Professional management and diversification for small investors",
                    "Lower minimum investment than building diversified portfolio directly",
                    "Come in many varieties (equity, debt, hybrid, index funds)"
                ],
                "advantages": ["Professional management", "Diversification", "Low minimums", "Liquidity"],
                "disadvantages": ["Management fees", "No control over holdings", "Tax inefficiency"],
                "types": ["Equity funds", "Debt funds", "Hybrid funds", "Index funds"],
                "related_concepts": ["expense_ratio", "nav", "systematic_investment_plan"]
            },
            
            "etf": {
                "definition": "Exchange-Traded Funds are investment funds traded on stock exchanges like individual stocks, typically tracking an index.",
                "key_points": [
                    "Combine benefits of mutual funds and individual stocks",
                    "Generally lower fees than actively managed mutual funds",
                    "Can be bought and sold throughout trading hours"
                ],
                "advantages": ["Low costs", "Tax efficiency", "Flexibility", "Transparency"],
                "popular_types": ["S&P 500 ETFs", "Bond ETFs", "Sector ETFs", "International ETFs"],
                "vs_mutual_funds": "ETFs trade intraday, usually lower fees, more tax efficient",
                "related_concepts": ["index_investing", "passive_investing", "expense_ratio"]
            },
            
            # Financial Ratios & Metrics
            "pe_ratio": {
                "definition": "Price-to-Earnings ratio measures a company's share price relative to its earnings per share, indicating how much investors pay for each dollar of earnings.",
                "key_points": [
                    "Higher P/E suggests investors expect higher growth",
                    "Can indicate overvaluation or undervaluation",
                    "Should be compared to industry averages and historical levels"
                ],
                "formula": "P/E Ratio = Market Price per Share / Earnings per Share",
                "interpretation": {
                    "Low P/E (< 15)": "May be undervalued or facing challenges",
                    "Medium P/E (15-25)": "Fairly valued for most mature companies",
                    "High P/E (> 25)": "High growth expectations or potentially overvalued"
                },
                "limitations": ["Based on past earnings", "Doesn't account for growth", "Industry variations"],
                "related_concepts": ["earnings_per_share", "valuation", "growth_stocks"]
            },
            
            "roe": {
                "definition": "Return on Equity measures how efficiently a company uses shareholders' equity to generate profits.",
                "key_points": [
                    "Higher ROE generally indicates better management efficiency",
                    "Should be compared to industry peers",
                    "Can be artificially inflated by high debt levels"
                ],
                "formula": "ROE = Net Income / Shareholders' Equity × 100%",
                "interpretation": {
                    "Excellent": "> 20%",
                    "Good": "15-20%",
                    "Average": "10-15%",
                    "Poor": "< 10%"
                },
                "related_concepts": ["roa", "profit_margin", "financial_leverage"]
            },
            
            # Investment Strategies
            "dollar_cost_averaging": {
                "definition": "Investment strategy of regularly investing fixed amounts regardless of market conditions to reduce the impact of volatility.",
                "key_points": [
                    "Reduces timing risk by spreading purchases over time",
                    "Particularly effective in volatile markets",
                    "Requires discipline to continue during market downturns"
                ],
                "example": "Investing ₹5,000 monthly in an index fund for 20 years, regardless of market ups and downs.",
                "advantages": ["Reduces timing risk", "Enforces discipline", "Simple to implement"],
                "disadvantages": ["May underperform lump sum in rising markets", "Transaction costs"],
                "related_concepts": ["systematic_investment_plan", "market_timing", "volatility"]
            },
            
            "asset_allocation": {
                "definition": "The strategic distribution of investments across different asset classes (stocks, bonds, cash) based on goals, time horizon, and risk tolerance.",
                "key_points": [
                    "More important than individual security selection",
                    "Should change as you age and circumstances change",
                    "Balances growth potential with risk management"
                ],
                "common_models": {
                    "Conservative (Age 60+)": "30% stocks, 60% bonds, 10% cash",
                    "Moderate (Age 40-60)": "60% stocks, 35% bonds, 5% cash",
                    "Aggressive (Age 20-40)": "80% stocks, 15% bonds, 5% cash"
                },
                "rebalancing": "Periodically adjusting back to target allocation",
                "related_concepts": ["risk_tolerance", "time_horizon", "rebalancing"]
            },
            
            # Market Concepts
            "market_volatility": {
                "definition": "The degree of variation in trading prices over time, measuring how much and how quickly prices move up and down.",
                "key_points": [
                    "Normal part of market behavior",
                    "Can create opportunities for patient investors",
                    "Higher volatility generally means higher risk"
                ],
                "causes": ["Economic data", "Company earnings", "Geopolitical events", "Market sentiment"],
                "measurement": "Standard deviation of returns over time",
                "management": ["Diversification", "Long-term focus", "Dollar-cost averaging"],
                "related_concepts": ["risk", "standard_deviation", "beta"]
            },
            
            "inflation": {
                "definition": "The general increase in prices of goods and services over time, reducing the purchasing power of money.",
                "key_points": [
                    "Erodes the real value of money over time",
                    "Investments should aim to beat inflation rate",
                    "Moderate inflation (2-3%) is considered healthy for economy"
                ],
                "impact_on_investments": {
                    "Stocks": "Generally good hedge against inflation long-term",
                    "Bonds": "Fixed payments lose value in inflationary periods",
                    "Real Estate": "Often appreciates with inflation"
                },
                "protection_strategies": ["Equity investments", "TIPS (Treasury Inflation-Protected Securities)", "Real assets"],
                "related_concepts": ["real_return", "purchasing_power", "tips"]
            }
        }
    
    def get_concept(self, concept_key: str) -> Dict:
        """Retrieve information about a specific financial concept"""
        return self.knowledge_base.get(concept_key.lower(), {})
    
    def search_concepts(self, query: str) -> List[str]:
        """Search for concepts related to a query"""
        query_lower = query.lower()
        matches = []
        
        # Direct matches
        for concept_key in self.knowledge_base.keys():
            if concept_key.replace('_', ' ') in query_lower or query_lower in concept_key:
                matches.append(concept_key)
        
        # Search in definitions and key points
        for concept_key, concept_data in self.knowledge_base.items():
            definition = concept_data.get('definition', '').lower()
            key_points = ' '.join(concept_data.get('key_points', [])).lower()
            
            if any(term in definition or term in key_points for term in query_lower.split()):
                if concept_key not in matches:
                    matches.append(concept_key)
        
        return matches[:3]  # Return top 3 matches

    def get_all_concepts(self) -> List[str]:
        """Get list of all available concepts"""
        return list(self.knowledge_base.keys())
