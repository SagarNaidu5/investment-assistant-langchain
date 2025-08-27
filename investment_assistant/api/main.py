from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import time
import logging

from ..production.enhanced_graph import production_graph
from ..production.monitoring import metrics
from ..production.config import config

logger = logging.getLogger(__name__)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's investment question")
    conversation_history: Optional[List[str]] = Field(default=[], description="Previous conversation context")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    request_id: str
    response_time: float
    
    # Intent-specific fields (optional)
    risk_tolerance: Optional[str] = None
    recommended_allocation: Optional[dict] = None
    stock_symbol: Optional[str] = None
    recommendation: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    requests_processed: int
    error_rate: float
    avg_response_time: float

# FastAPI app
app = FastAPI(
    title="Investment Assistant API",
    description="AI-powered investment advisory and education platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting (simple in-memory implementation)
request_times = {}

async def rate_limit_check(request: ChatRequest):
    """Simple rate limiting"""
    if not config.api_key_required:  # Skip rate limiting in development
        return
    
    user_id = request.user_id or "anonymous"
    now = time.time()
    
    # Clean old requests
    if user_id in request_times:
        request_times[user_id] = [t for t in request_times[user_id] if now - t < 60]
    else:
        request_times[user_id] = []
    
    # Check rate limits
    recent_requests = len(request_times[user_id])
    if recent_requests >= config.max_requests_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_times[user_id].append(now)

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    rate_check: None = Depends(rate_limit_check)
):
    """Main chat endpoint for investment assistant"""
    try:
        start_time = time.time()
        
        result = production_graph.invoke({
            "user_message": request.message,
            "conversation_history": request.conversation_history
        })
        
        response = ChatResponse(
            response=result.get("response", result.get("market_analysis", "No response generated")),
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            request_id=result.get("request_id", "unknown"),
            response_time=result.get("response_time", time.time() - start_time),
            
            # Optional intent-specific fields
            risk_tolerance=result.get("risk_tolerance"),
            recommended_allocation=result.get("recommended_allocation"),
            stock_symbol=result.get("stock_symbol"),
            recommendation=result.get("recommendation")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """Health check endpoint"""
    try:
        health_data = production_graph.get_health_status()
        
        return HealthResponse(
            status=health_data["status"],
            timestamp=health_data["timestamp"],
            uptime=health_data["uptime"],
            requests_processed=health_data["requests_processed"],
            error_rate=health_data["error_rate"],
            avg_response_time=health_data["avg_response_time"]
        )
    except Exception as e:
        logger.error(f"Health endpoint error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=time.time(),
            uptime=0,
            requests_processed=0,
            error_rate=1.0,
            avg_response_time=0
        )

@app.get("/metrics")
async def metrics_endpoint():
    """Detailed metrics endpoint (admin only in production)"""
    if config.environment == "production":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "metrics": metrics.get_metrics_summary(),
        "performance": production_graph.performance.get_component_stats()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Investment Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if config.debug else "disabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
