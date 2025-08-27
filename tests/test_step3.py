import pytest
from investment_assistant.graph import investment_graph

def test_portfolio_creation_flow():
    """Test complete portfolio creation flow"""
    
    result = investment_graph.invoke({
        "user_message": "Build me an aggressive portfolio, I'm 30 years old",
        "conversation_history": []
    })
    
    # Should route to portfolio creation
    assert result["intent"] == "portfolio_creation"
    assert result["confidence"] > 0.7
    
    # Should have portfolio data
    assert "recommended_allocation" in result
    assert "etf_selection" in result
    assert "builder_reasoning" in result
    
    # Allocation should sum to 1
    alloc = result["recommended_allocation"]
    assert abs(sum(alloc.values()) - 1.0) < 0.01
    
    # Should have ETFs with weights
    etfs = result["etf_selection"]
    assert len(etfs) > 0
    total_weight = sum(etf["weight"] for etf in etfs)
    assert abs(total_weight - 1.0) < 0.01

def test_profile_then_portfolio():
    """Test profile analysis followed by portfolio creation"""
    
    # First analyze profile
    profile_result = investment_graph.invoke({
        "user_message": "I'm 35, moderate risk tolerance, saving for retirement",
        "conversation_history": []
    })
    
    assert profile_result["intent"] == "profile_analysis"
    assert profile_result["risk_tolerance"] == "moderate"
    
    # Then build portfolio using same profile data
    portfolio_result = investment_graph.invoke({
        "user_message": "Build me a portfolio based on this profile",
        "conversation_history": [],
        "risk_tolerance": "moderate",
        "age_range": "young",
        "investment_horizon": "long"
    })
    
    assert portfolio_result["intent"] == "portfolio_creation"
    assert "recommended_allocation" in portfolio_result

if __name__ == "__main__":
    pytest.main([__file__])
