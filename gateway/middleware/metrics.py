# ============================================================================
# OBSERVABILITY - PROMETHEUS METRICS (utils/metrics.py)
# ============================================================================
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response
import time
from functools import wraps

# Metrics
request_count = Counter(
    'chatbot_requests_total',
    'Total number of requests',
    ['service', 'endpoint', 'status']
)

request_duration = Histogram(
    'chatbot_request_duration_seconds',
    'Request duration in seconds',
    ['service', 'endpoint']
)

active_sessions = Gauge(
    'chatbot_active_sessions',
    'Number of active chat sessions',
    ['service']
)

llm_latency = Histogram(
    'llm_response_latency_seconds',
    'LLM response latency',
    ['model']
)

intent_classification_accuracy = Gauge(
    'intent_classification_accuracy',
    'Intent classification accuracy',
    ['intent']
)

escalation_rate = Counter(
    'chatbot_escalations_total',
    'Total number of escalations to human agents',
    ['reason']
)

def track_metrics(service: str, endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                request_count.labels(
                    service=service,
                    endpoint=endpoint,
                    status=status
                ).inc()
                request_duration.labels(
                    service=service,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator

# Metrics endpoint
def setup_metrics_endpoint(app: FastAPI):
    @app.get("/metrics")
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type="text/plain"
        )