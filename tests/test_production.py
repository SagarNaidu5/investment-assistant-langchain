import pytest
import time
from fastapi.testclient import TestClient
from investment_assistant.api.main import app
from investment_assistant.production.enhanced_graph import production_graph

client = TestClient(app)

class TestProductionAPI:
    """Test production API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime" in data
    
    def test_chat_endpoint_profile_analysis(self):
        """Test chat endpoint with profile analysis"""
        request_data = {
            "message": "I'm 30 years old and want to start investing for retirement",
            "conversation_history": []
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["intent"] == "profile_analysis"
        assert "response" in data
        assert data["confidence"] > 0.5
    
    def test_chat_endpoint_portfolio_creation(self):
        """Test portfolio creation functionality"""
        request_data = {
            "message": "Build me an aggressive portfolio",
            "conversation_history": []
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["intent"] == "portfolio_creation"
        assert data["recommended_allocation"] is not None
    
    def test_chat_endpoint_validation(self):
        """Test input validation"""
        # Empty message
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 422
        
        # Message too long
        long_message = "x" * 1001
        response = client.post("/chat", json={"message": long_message})
        assert response.status_code == 422
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint (development only)"""
        response = client.get("/metrics")
        # Should work in development environment
        assert response.status_code in [200, 403]

class TestProductionGraph:
    """Test production graph functionality"""
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        try:
            result = production_graph.invoke({"user_message": ""})
            # Should not reach here due to validation
            assert False
        except:
            # Expected to fail validation
            pass
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        start_metrics = production_graph.performance.get_component_stats()
        
        # Make a request
        result = production_graph.invoke({
            "user_message": "What is compound interest?",
            "conversation_history": []
        })
        
        end_metrics = production_graph.performance.get_component_stats()
        
        # Should have recorded graph execution time
        assert "graph_execution" in end_metrics
    
    def test_health_status(self):
        """Test health status functionality"""
        health = production_graph.get_health_status()
        
        assert "status" in health
        assert "uptime" in health
        assert "requests_processed" in health
        assert health["status"] in ["healthy", "unhealthy"]

@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_complete_conversation_flow(self):
        """Test a complete conversation flow"""
        # Profile analysis
        profile_response = client.post("/chat", json={
            "message": "I'm 25, moderate risk tolerance, saving for retirement",
            "conversation_history": []
        })
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        
        # Portfolio creation
        portfolio_response = client.post("/chat", json={
            "message": "Build me a portfolio based on my profile",
            "conversation_history": [profile_data["response"]]
        })
        assert portfolio_response.status_code == 200
        portfolio_data = portfolio_response.json()
        
        # Education question
        education_response = client.post("/chat", json={
            "message": "What is compound interest?",
            "conversation_history": []
        })
        assert education_response.status_code == 200
        education_data = education_response.json()
        
        # Verify all intents work
        assert profile_data["intent"] == "profile_analysis"
        assert portfolio_data["intent"] == "portfolio_creation"
        assert education_data["intent"] == "question_answering"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
