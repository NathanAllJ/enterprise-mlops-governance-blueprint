# src/api_gateway.py
import time
from pydantic import BaseModel, Field

class InferencePayload(BaseModel):
    """Enforces explicit data contract validation at edge entrypoints."""
    age: int = Field(..., ge=18, le=110, description="Customer age")
    monthly_charges: float = Field(..., ge=0.0, description="Monthly invoice total")


class MLServiceCircuitBreaker:
    """Enterprise self-healing rule engine to detect system or database faults."""
    def __init__(self, failure_threshold: int = 3, recovery_time_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED (Normal), OPEN (Failing), HALF-OPEN (Recovery mode)

    def can_execute(self) -> bool:
        """Determines if the main model interface is healthy or tripped."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = "HALF-OPEN"
                return True
            return False
        return True

    def handle_failure(self):
        """Increments error counts and flips switch if threshold is crossed."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print("🚨 [CIRCUIT BREAKER OPENED]: Main model layer offline. Falling back to safety rules.")

    def handle_success(self):
        """Resets the circuit parameters upon verified clean system operation."""
        self.failure_count = 0
        self.state = "CLOSED"


class APIRoutingGateway:
    def __init__(self):
        # Instantiate a dedicated circuit breaker for tracking inference routing failures
        self.circuit_breaker = MLServiceCircuitBreaker(failure_threshold=3, recovery_time_seconds=30)

    def process_prediction(self, model, features: InferencePayload) -> dict:
        """Transforms payload data into clean formats for model scoring loops with fallback protections."""
        
        # 1. Enforce Gateway Circuit Check
        if not self.circuit_breaker.can_execute():
            # Conservative rule fallback if backend services are offline
            fallback_prediction = 1 if features.monthly_charges > 100.0 else 0
            return {
                "prediction": fallback_prediction,
                "confidence_score": 0.50,
                "status": "FALLBACK_SAFETY_MODE_ACTIVE",
                "warning": "Primary ML engine isolated due to consecutive service degradation faults."
            }

        # 2. Run Standard Model Inference Pipeline
        try:
            if model is None:
                raise RuntimeError("Target production model object uninitialized inside RAM container memory context.")
                
            input_data = [[features.age, features.monthly_charges]]
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0][prediction]
            
            # Reset counters upon verified clean transaction run
            self.circuit_breaker.handle_success()
            
            return {
                "prediction": int(prediction),
                "confidence_score": float(probability),
                "status": "PROCESSED_SUCCESSFULLY"
            }
            
        except Exception as e:
            # Trip the gate, track fault occurrence metrics, and pass failure to the caller trace
            self.circuit_breaker.handle_failure()
            return {
                "prediction": -1,
                "confidence_score": 0.0,
                "status": "INTERNAL_INFERENCE_FAILURE",
                "error_details": str(e)
            }
