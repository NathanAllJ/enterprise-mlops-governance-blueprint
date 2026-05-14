# data_pipeline/validator.py
import pandas as pd
from typing import Dict, Any

class DataValidator:
    def __init__(self):
        # Explicit schemas prevent data mutation issues downstream
        self.expected_features = {
            "customer_id": "object",
            "age": "int64",
            "monthly_charges": "float64",
            "email": "object",
            "account_status": "object"
        }

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validates that incoming columns meet required enterprise types."""
        if df.empty:
            raise ValueError("❌ Ingested dataframe payload is completely empty.")

        for column, expected_type in self.expected_features.items():
            if column not in df.columns:
                raise KeyError(f"❌ Missing mandatory structural feature column: {column}")
            
            # Basic validation of data types
            if df[column].dtype != expected_type:
                try:
                    df[column] = df[column].astype(expected_type)
                except Exception:
                    raise TypeError(f"❌ Column '{column}' failed strict type conformity to: {expected_type}")
                    
        print("✅ [SCHEMA VALIDATION]: Complete. Schema shapes conform to specification.")
        return True

    def enforce_domain_bounds(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensures numeric domains contain realistic values to stop data poisoning."""
        # Clean out structural anomalies or corrupted entries
        df = df[(df['age'] >= 18) & (df['age'] <= 110)]
        df = df[df['monthly_charges'] >= 0.0]
        
        print("✅ [DOMAIN GUARDRAILS]: Complete. Out-of-bounds metrics successfully pruned.")
        return df

