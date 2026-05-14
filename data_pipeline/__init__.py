# data_pipeline/__init__.py

"""
Enterprise Data Pipeline Module
Exposes core data validation, adversarial screening, anonymization, and ingestion orchestration managers.
"""

from .validator import DataValidator
from .anonymizer import DataAnonymizer
from .pipeline_manager import EnterprisePipelineManager

# Explicitly defines what is exposed when an engineer types: from data_pipeline import *
__all__ = [
    "DataValidator",
    "DataAnonymizer",
    "EnterprisePipelineManager"
]

__version__ = "1.1.0"
