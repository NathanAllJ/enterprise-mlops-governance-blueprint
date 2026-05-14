# src/app.py
from fastapi import FastAPI, HTTPException
from src.api_gateway import InferencePayload, APIRoutingGateway
from src.model_registry import EnterpriseModelRegistry

app = FastAPI(title="Enterprise ML Core Inference Engine", version="1.2.0")

# Instantiate single gateway router persistence context
gateway = APIRoutingGateway()

try:
    registry = EnterpriseModelRegistry()
    production_model = registry.load_latest_model(version="1.0.0")
except Exception:
    production_model = None

@app.get("/health", tags=["Infrastructure"])
def health_check():
    return {"status": "ONLINE", "circuit_state": gateway.circuit_breaker.state}

@app.post("/predict", tags=["Inference"])
def predict_endpoint(payload: InferencePayload):
    """Processes network inference transactions through our self-healing API Gateway component."""
    response = gateway.process_prediction(production_model, payload)
    
    if response["status"] == "INTERNAL_INFERENCE_FAILURE":
        raise HTTPException(status_code=503, detail=response["error_details"])
        
    return response
