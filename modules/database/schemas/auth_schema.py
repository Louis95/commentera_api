"""Auth schema"""
from pydantic import BaseModel, Field


class GenerateToken(BaseModel):
    """
    Represents the data needed to generate a token.
    """

    customer_alias: str = Field(
        ...,
        description="Customer alias. You can get a sample alias from the csv",
    )
