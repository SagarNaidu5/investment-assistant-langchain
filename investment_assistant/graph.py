from typing import TypedDict, Literal, Dict, List, Any
from langgraph.graph import StateGraph, END
from .nodes.router import router_node
from .nodes.profile_analyzer import profile_analyzer_node
from .nodes.portfolio_builder import portfolio_builder_node
from .nodes.market_researcher import market_researcher_node
from .nodes.question_answerer import question_answerer_node


class InvestmentState(TypedDict):
    # User input
    user_message: str
    conversation_history: list[str]
    
    # Routing
    intent: Literal["profile_analysis", "portfolio_creation", "market_research", "question_answering"]
    confidence: float
    
    # Profile data
    risk_tolerance: str  # "conservative", "moderate", "aggressive"
    investment_horizon: str  # "short", "medium", "long"
    age_range: str
    income_level: str
    investment_goals: list[str]
    reasoning: str
    
    # Portfolio data
    recommended_allocation: Dict[str, float]
    etf_selection: List[Dict[str, Any]]
    builder_reasoning: str
    
    # Market Research data
    stock_symbol: str
    current_price: float
    price_change_pct: float
    technical_signals: Dict[str, str]  # {"RSI": "oversold", "MACD": "bullish"}
    fundamental_ratios: Dict[str, float]  # {"PE": 15.2, "ROE": 0.18}
    market_analysis: str
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence_score: float

    # Final output
    response: str
    next_action: str

def route_decision(state):
    """Decide which node to route to based on intent"""
    intent = state.get("intent", "question_answering")
    
    if intent == "profile_analysis":
        return "profile_analyzer"
    elif intent == "portfolio_creation":
        return "portfolio_builder"
    elif intent == "market_research":
        return "market_researcher"  # Not implemented yet, go to end
    else:
        return "question_answerer"  # Not implemented yet, go to end

# Build the graph
graph = StateGraph(InvestmentState)

# Add nodes
graph.add_node("router", router_node)
graph.add_node("profile_analyzer", profile_analyzer_node)
graph.add_node("portfolio_builder", portfolio_builder_node)
graph.add_node("market_researcher", market_researcher_node)
graph.add_node("question_answerer", question_answerer_node)

# Add edges
graph.set_entry_point("router")

# Conditional routing from router
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "profile_analyzer": "profile_analyzer",
        "portfolio_builder": "portfolio_builder",
        "market_researcher": "market_researcher",
        "question_answerer": "question_answerer",
        END: END
    }
)

# Direct edges to end after processing
graph.add_edge("profile_analyzer", END)
graph.add_edge("portfolio_builder", END)
graph.add_edge("market_researcher", END)
graph.add_edge("question_answerer", END)
# Compile the graph
investment_graph = graph.compile()
