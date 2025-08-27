from typing import Dict, Any
import time
from ..graph import investment_graph as base_graph
from .error_handling import with_error_handling, safe_graph_invoke, ValidationError
from .monitoring import metrics, performance
from .config import config
import logging

logger = logging.getLogger(__name__)

class ProductionInvestmentGraph:
    """Production-ready wrapper for Investment Assistant graph"""
    
    def __init__(self):
        self.graph = base_graph
        self.request_count = 0
        self.performance = performance  # Add this line - reference to global performance monitor
    
    @with_error_handling(
        retries=2, 
        delay=1.0, 
        fallback_response={
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            "intent": "error",
            "confidence": 0.0
        }
    )
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Production invoke with monitoring and error handling"""
        start_time = time.time()
        self.request_count += 1
        request_id = f"req_{int(start_time)}_{self.request_count}"
        
        logger.info(f"Processing request {request_id}: {input_data.get('user_message', '')[:100]}")
        
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Add request metadata
            enhanced_input = {
                **input_data,
                "request_id": request_id,
                "timestamp": start_time
            }
            
            # Time the graph execution
            with self.performance.time_component("graph_execution"):
                result = self.graph.invoke(enhanced_input)
            
            # Record successful request
            response_time = time.time() - start_time
            intent = result.get("intent", "unknown")
            
            metrics.record_request(intent, response_time, success=True)
            
            # Add response metadata
            result["request_id"] = request_id
            result["response_time"] = response_time
            
            logger.info(f"Completed request {request_id} in {response_time:.2f}s with intent: {intent}")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            metrics.record_request("error", response_time, success=False)
            
            logger.error(f"Request {request_id} failed after {response_time:.2f}s: {str(e)}")
            raise
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data"""
        required_fields = ["user_message"]
        
        for field in required_fields:
            if field not in input_data:
                raise ValidationError(f"Missing required field: {field}")
        
        user_message = input_data["user_message"]
        
        if not isinstance(user_message, str):
            raise ValidationError("user_message must be a string")
        
        if len(user_message.strip()) == 0:
            raise ValidationError("user_message cannot be empty")
        
        if len(user_message) > 1000:  # Reasonable limit
            raise ValidationError("user_message too long (max 1000 characters)")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            # Test basic functionality
            test_result = self.invoke({
                "user_message": "What is compound interest?",
                "conversation_history": []
            })
            
            api_healthy = test_result.get("intent") != "error"
        except:
            api_healthy = False
        
        metrics_summary = metrics.get_metrics_summary()
        
        return {
            "status": "healthy" if api_healthy else "unhealthy",
            "timestamp": time.time(),
            "uptime": metrics_summary["uptime_seconds"],
            "requests_processed": metrics_summary["requests"]["total"],
            "error_rate": metrics_summary["errors"]["rate"],
            "avg_response_time": metrics_summary["requests"]["avg_response_time"],
            "system_cpu": metrics_summary["system"]["cpu_usage"],
            "system_memory": metrics_summary["system"]["memory_usage"],
            "components": self.performance.get_component_stats()  # Use self.performance
        }

# Create production graph instance
production_graph = ProductionInvestmentGraph()
