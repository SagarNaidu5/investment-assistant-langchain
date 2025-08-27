import time
import psutil
import threading
from typing import Dict, Any, List
from collections import defaultdict, deque
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and track system and application metrics"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics = defaultdict(lambda: deque(maxlen=window_size))
        self.counters = defaultdict(int)
        self.start_time = time.time()
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self.monitoring_thread.start()
    
    def record_request(self, intent: str, response_time: float, success: bool = True):
        """Record a request with timing and success metrics"""
        timestamp = time.time()
        
        self.metrics["response_times"].append(response_time)
        self.metrics["requests_per_minute"].append(timestamp)
        
        self.counters["total_requests"] += 1
        self.counters[f"intent_{intent}"] += 1
        
        if success:
            self.counters["successful_requests"] += 1
        else:
            self.counters["failed_requests"] += 1
    
    def record_llm_usage(self, model: str, tokens_used: int, cost: float = 0.0):
        """Record LLM usage metrics"""
        self.metrics["llm_tokens"].append(tokens_used)
        self.counters["total_tokens"] += tokens_used
        self.counters[f"tokens_{model}"] += tokens_used
        
        if cost > 0:
            self.metrics["llm_costs"].append(cost)
            self.counters["total_cost"] += cost
    
    def record_error(self, error_type: str, severity: str):
        """Record error metrics"""
        self.counters[f"error_{error_type}"] += 1
        self.counters[f"severity_{severity}"] += 1
        self.counters["total_errors"] += 1
    
    def _background_monitoring(self):
        """Background system monitoring"""
        while True:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                self.metrics["cpu_usage"].append(cpu_percent)
                self.metrics["memory_usage"].append(memory_percent)
                self.metrics["disk_usage"].append(disk_percent)
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        now = time.time()
        uptime = now - self.start_time
        
        # Calculate rates
        recent_requests = [t for t in self.metrics["requests_per_minute"] 
                          if now - t < 60]  # Last minute
        requests_per_minute = len(recent_requests)
        
        response_times = list(self.metrics["response_times"])
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "uptime_seconds": uptime,
            "system": {
                "cpu_usage": list(self.metrics["cpu_usage"])[-1] if self.metrics["cpu_usage"] else 0,
                "memory_usage": list(self.metrics["memory_usage"])[-1] if self.metrics["memory_usage"] else 0,
                "disk_usage": list(self.metrics["disk_usage"])[-1] if self.metrics["disk_usage"] else 0,
            },
            "requests": {
                "total": self.counters["total_requests"],
                "successful": self.counters["successful_requests"],
                "failed": self.counters["failed_requests"],
                "per_minute": requests_per_minute,
                "avg_response_time": avg_response_time,
            },
            "llm": {
                "total_tokens": self.counters["total_tokens"],
                "total_cost": self.counters.get("total_cost", 0),
                "avg_tokens_per_request": (
                    self.counters["total_tokens"] / max(self.counters["total_requests"], 1)
                ),
            },
            "errors": {
                "total": self.counters["total_errors"],
                "rate": self.counters["total_errors"] / max(self.counters["total_requests"], 1),
            },
            "intents": {
                key.replace("intent_", ""): value 
                for key, value in self.counters.items() 
                if key.startswith("intent_")
            }
        }

# Global metrics collector
metrics = MetricsCollector()

class PerformanceMonitor:
    """Monitor performance of individual components"""
    
    def __init__(self):
        self.component_metrics = defaultdict(list)
    
    def time_component(self, component_name: str):
        """Context manager for timing components"""
        return ComponentTimer(component_name, self)
    
    def record_component_time(self, component_name: str, duration: float):
        """Record component execution time"""
        self.component_metrics[component_name].append({
            "duration": duration,
            "timestamp": time.time()
        })
        
        # Keep only recent entries (last 100)
        if len(self.component_metrics[component_name]) > 100:
            self.component_metrics[component_name] = self.component_metrics[component_name][-100:]
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all components"""
        stats = {}
        
        for component, measurements in self.component_metrics.items():
            if measurements:
                durations = [m["duration"] for m in measurements]
                stats[component] = {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "last_duration": durations[-1] if durations else 0
                }
        
        return stats

class ComponentTimer:
    """Context manager for timing component execution"""
    
    def __init__(self, component_name: str, monitor: PerformanceMonitor):
        self.component_name = component_name
        self.monitor = monitor
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.monitor.record_component_time(self.component_name, duration)

# Global performance monitor
performance = PerformanceMonitor()
