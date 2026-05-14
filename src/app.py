# src/app.py
from fastapi import FastAPI, HTTPException
from src.api_gateway import InferencePayload, APIRoutingGateway
from src.model_registry import EnterpriseModelRegistry

app = FastAPI(
    title="Enterprise ML Core Inference Engine",
    description="Production microservice API serving versioned model predictions.",
    version="1.0.0"
)

# Initialize registry and preload model artifact to RAM for fast request speeds
try:
    registry = EnterpriseModelRegistry()
    production_model = registry.load_latest_model(version="1.0.0")
except Exception:
    print("Warning: Model artifact v1.0.0 not preloaded. Execute train.py first.")
    production_model = None

@app.get("/health", tags=["Infrastructure"])
def health_check():
    """Kubernetes liveness and readiness monitoring endpoint probe."""
    if production_model is None:
        raise HTTPException(status_code=503, detail="Model artifact is currently offline or uninitialized.")
    return {"status": "ONLINE", "model_version": "1.0.0"}

@app.post("/predict", tags=["Inference"])
def predict_endpoint(payload: InferencePayload):
    """Exposes real-time model interface queries securely to internal networks."""
    if production_model is None:
        raise HTTPException(status_code=503, detail="Serving model binary is unavailable.")
    
    try:
        results = APIRoutingGateway.process_prediction(production_model, payload)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal inference failure: {str(e)}")

