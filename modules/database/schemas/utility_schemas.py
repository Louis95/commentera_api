"""Schemas for various utility purposes"""
from pydantic import BaseModel, Field


class SuccessfulResponseOut(BaseModel):
    """Successful response schema"""

    status_code: int = Field(
        ..., description="Status code of response", gte=200, lte=299
    )
    message: str = Field(..., description="Message of response")
