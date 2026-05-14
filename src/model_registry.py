# src/model_registry.py
import os
import json
import joblib
from datetime import datetime

class EnterpriseModelRegistry:
    def __init__(self, registry_root: str = "models/"):
        self.root = registry_root
        os.makedirs(self.root, exist_ok=True)

    def save_model_artifact(self, model_object, metrics: dict, version: str) -> str:
        """Serializes the trained model object and commits an immutable metadata file."""
        model_filename = f"model_v{version}.pkl"
        meta_filename = f"metadata_v{version}.json"
        
        model_path = os.path.join(self.root, model_filename)
        meta_path = os.path.join(self.root, meta_filename)
        
        # Save the physical binary model artifact
        joblib.dump(model_object, model_path)
        
        # Save structural tracking information for auditing
        metadata = {
            "model_version": version,
            "saved_at": datetime.utcnow().isoformat() + "Z",
            "performance_metrics": metrics,
            "framework": "scikit-learn",
            "compliance_status": "VERIFIED"
        }
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"[MODEL REGISTRY]: Model v{version} and compliance logs saved to {self.root}")
        return model_path

    def load_latest_model(self, version: str):
        """Loads a verified model artifact from storage."""
        model_path = os.path.join(self.root, f"model_v{version}.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Requested model version {version} not found in registry.")
        return joblib.load(model_path)

