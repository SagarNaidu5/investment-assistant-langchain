import pytest
from investment_assistant.graph import investment_graph

def test_profile_analysis_routing():
    """Test that profile-related queries route correctly"""
    
    test_cases = [
        {
            "input": "I'm 28 years old and want to start investing for retirement",
            "expected_intent": "profile_analysis"
        },
        {
            "input": "I have a moderate risk tolerance and 20 year timeline",
            "expected_intent": "profile_analysis"
        }
    ]
    
    for case in test_cases:
        result = investment_graph.invoke({
            "user_message": case["input"],
            "conversation_history": []
        })
        
        assert result["intent"] == case["expected_intent"]
        assert result["confidence"] > 0.7

def test_profile_extraction():
    """Test profile analyzer extracts correct information"""
    
    user_input = "I'm 30 years old, make 80k per year, and want to invest for retirement. I'm okay with some risk but don't want to lose everything."
    
    result = investment_graph.invoke({
        "user_message": user_input,
        "conversation_history": []
    })
    
    # Should extract reasonable profile data
    assert result.get("risk_tolerance") in ["conservative", "moderate", "aggressive"]
    assert result.get("age_range") == "young"
    assert "retirement" in result.get("investment_goals", [])

def test_portfolio_builder():
    result = investment_graph.invoke({
        "user_message": "I'm 35 with aggressive risk appetite. Build me a portfolio.",
        "conversation_history": [],
        "intent": "portfolio_creation",
        "risk_tolerance": "aggressive",
        "age_range": "young"
    })
    alloc = result["recommended_allocation"]
    assert 0.75 <= alloc["equity"] <= 0.9
    assert sum(w["weight"] for w in result["etf_selection"]) == pytest.approx(1.0, abs=1e-6)

