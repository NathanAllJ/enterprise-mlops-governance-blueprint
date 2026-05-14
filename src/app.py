# src/app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from src.api_gateway import InferencePayload, APIRoutingGateway
from src.model_registry import EnterpriseModelRegistry

app = FastAPI(
    title="Enterprise ML Core Inference Engine", 
    description="Production microservice API serving versioned model predictions with integrated resilience and concurrency patterns.",
    version="1.3.0"
)

# Instantiate a single gateway router persistence context to preserve Circuit Breaker state across requests
gateway = APIRoutingGateway()

try:
    registry = EnterpriseModelRegistry()
    production_model = registry.load_latest_model(version="1.0.0")
except Exception:
    print("Warning: Primary model artifact v1.0.0 uninitialized or unavailable.")
    production_model = None


@app.get("/health", tags=["Infrastructure"])
def health_check():
    """Kubernetes liveness and readiness monitoring endpoint probe."""
    return {
        "status": "ONLINE" if production_model is not None else "DEGRADED",
        "circuit_state": gateway.circuit_breaker.state
    }


@app.post("/predict", tags=["Inference"])
def predict_endpoint(payload: InferencePayload):
    """Processes real-time inference transactions synchronously through the self-healing API Gateway."""
    response = gateway.process_prediction(production_model, payload)
    
    if response["status"] == "INTERNAL_INFERENCE_FAILURE":
        raise HTTPException(status_code=503, detail=response["error_details"])
        
    return response


@app.post("/predict/async", tags=["Inference"])
async def predict_async_endpoint(payload: InferencePayload, background_tasks: BackgroundTasks):
    """Processes heavy inferencing asynchronously using concurrent worker threads to avoid blocking server runtimes."""
    
    # Define a clean internal worker to decouple execution from the direct network thread pool
    def heavy_inference_worker(data: InferencePayload):
        print(f"Background worker picked up concurrent inference execution task thread...")
        worker_response = gateway.process_prediction(production_model, data)
        print(f"Async Job Execution Metrics Complete. Status: {worker_response['status']}")
        return worker_response

    # Offload the execution to FastAPI's background thread pool instantly
    background_tasks.add_task(heavy_inference_worker, payload)
    
    return {
        "status": "QUEUED", 
        "message": "Inference task off-loaded to non-blocking application background workers successfully.",
        "circuit_state": gateway.circuit_breaker.state
    }
