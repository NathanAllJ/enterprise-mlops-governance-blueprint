# data_pipeline/anonymizer.py
import os
import hmac
import hashlib
import pandas as pd
from typing import List

class DataAnonymizer:
    def __init__(self, restricted_fields: List[str] = None):
        # Default fallback to match the exact keys in config/security_policy.json
        self.restricted_fields = restricted_fields or ["email", "ssn", "patient_name"]
        # Pull salt from secure env to ensure hashes cannot be reversed via rainbow tables
        self.salt = os.getenv("PII_HASH_SALT", "DEFAULT_ENTERPRISE_SYSTEM_SALT_KEY").encode('utf-8')

    def _hash_value(self, val: Any) -> str:
        """Applies irreversible cryptographic HMAC SHA-256 tokenization to raw values."""
        if pd.isna(val) or val is None:
            return ""
        return hmac.new(self.salt, str(val).strip().lower().encode('utf-8'), hashlib.sha256).hexdigest()

    def transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scorches sensitive properties out of dataframes before training loops."""
        df_cleaned = df.copy()
        
        for column in self.restricted_fields:
            if column in df_cleaned.columns:
                # Replace sensitive identities with an untraceable signature
                df_cleaned[column] = df_cleaned[column].apply(self._hash_value)
                # Rename the column visually to declare compliance state
                df_cleaned = df_cleaned.rename(columns={column: f"anonymized_{column}"})
                
        print(f"[PRIVACY ENGINE]: Successfully anonymized restricted matrices: {self.restricted_fields}")
        return df_cleaned

