# tests/test_pipeline.py
import pytest
import pandas as pd
from data_pipeline import DataValidator

def test_data_validator_cleans_out_of_bounds_data():
    """Proves our CI/CD pipeline catches and purges poisoned data rows."""
    validator = DataValidator()
    
    # Setup standard input dataframe containing a corrupted row (Age 150)
    test_df = pd.DataFrame({
        "customer_id": ["C01", "C02"],
        "age": [34, 150], # 150 is out of legal bounds
        "monthly_charges": [50.0, 99.0],
        "email": ["test1@test.com", "test2@test.com"],
        "account_status": ["Active", "Active"]
    })
    
    # Run the validation block
    cleaned_df = validator.enforce_domain_bounds(test_df)
    
    # Assertions prove the invalid row was successfully removed
    assert len(cleaned_df) == 1
    assert cleaned_df["age"].iloc[0] == 34

