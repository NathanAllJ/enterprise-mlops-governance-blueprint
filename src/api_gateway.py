# src/api_gateway.py
from pydantic import BaseModel, Field

class InferencePayload(BaseModel):
    # Enforces explicit data contract validation at edge entrypoints
    age: int = Field(..., ge=18, le=110, description="Customer age")
    monthly_charges: float = Field(..., ge=0.0, description="Monthly invoice total")

class APIRoutingGateway:
    @staticmethod
    def process_prediction(model, features: InferencePayload) -> dict:
        """Transforms payload data into clean formats for model scoring loops."""
        input_data = [[features.age, features.monthly_charges]]
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][prediction]
        
        return {
            "prediction": int(prediction),
            "confidence_score": float(probability),
            "status": "PROCESSED_SUCCESSFULLY"
        }

