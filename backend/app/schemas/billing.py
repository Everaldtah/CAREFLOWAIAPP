"""
Billing Schemas
"""

from typing import Optional
from pydantic import BaseModel


class BillingCodeSuggestion(BaseModel):
    """Individual billing code suggestion."""
    code: str
    description: str
    confidence: float


class ICD10Suggestion(BaseModel):
    """ICD-10 diagnosis code suggestion."""
    code: str
    description: str
    confidence: float


class CPTSuggestion(BaseModel):
    """CPT procedure code suggestion."""
    code: str
    description: str
    confidence: float
