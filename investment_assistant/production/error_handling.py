import logging
import traceback
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InvestmentAssistantError(Exception):
    """Base exception for Investment Assistant"""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 error_code: Optional[str] = None, context: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = time.time()

class ModelTimeoutError(InvestmentAssistantError):
    """LLM model timeout error"""
    pass

class DataFetchError(InvestmentAssistantError):
    """External data source error"""
    pass

class ValidationError(InvestmentAssistantError):
    """Input validation error"""
    pass

class ConfigurationError(InvestmentAssistantError):
    """Configuration error"""
    pass

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_patterns = []
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with structured information"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": time.time(),
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        # Track error frequency
        error_key = f"{type(error).__name__}:{str(error)[:100]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log based on severity
        if isinstance(error, InvestmentAssistantError):
            if error.severity == ErrorSeverity.CRITICAL:
                logger.critical(json.dumps(error_info))
            elif error.severity == ErrorSeverity.HIGH:
                logger.error(json.dumps(error_info))
            elif error.severity == ErrorSeverity.MEDIUM:
                logger.warning(json.dumps(error_info))
            else:
                logger.info(json.dumps(error_info))
        else:
            logger.error(json.dumps(error_info))
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": dict(self.error_counts),
            "top_errors": sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }

# Global error handler
error_handler = ErrorHandler()

def with_error_handling(retries: int = 3, delay: float = 1.0, 
                       fallback_response: Optional[Dict] = None):
    """Decorator for robust error handling with retries"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except ModelTimeoutError as e:
                    last_exception = e
                    error_handler.log_error(e, {"attempt": attempt, "function": func.__name__})
                    if attempt < retries:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    break
                    
                except DataFetchError as e:
                    last_exception = e
                    error_handler.log_error(e, {"attempt": attempt, "function": func.__name__})
                    if attempt < retries:
                        time.sleep(delay)
                        continue
                    break
                    
                except ValidationError as e:
                    # Don't retry validation errors
                    error_handler.log_error(e, {"function": func.__name__})
                    break
                    
                except Exception as e:
                    last_exception = e
                    error_handler.log_error(e, {"attempt": attempt, "function": func.__name__})
                    if attempt < retries:
                        time.sleep(delay)
                        continue
                    break
            
            # All retries failed, return fallback or raise
            if fallback_response:
                logger.warning(f"Using fallback response for {func.__name__}")
                return fallback_response
            else:
                raise last_exception
        
        return wrapper
    return decorator

def safe_graph_invoke(graph, input_data: Dict, fallback_message: str = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."):
    """Safely invoke LangGraph with comprehensive error handling"""
    try:
        result = graph.invoke(input_data)
        return result
        
    except Exception as e:
        error_handler.log_error(e, {"input": input_data})
        
        # Return safe fallback response
        return {
            "response": fallback_message,
            "intent": "error",
            "error_occurred": True,
            "error_type": type(e).__name__
        }
