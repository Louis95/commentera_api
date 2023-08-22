"""Schemas for the message objects, used as responses"""
from pydantic import BaseModel, Field


class Message(BaseModel):
    detail: str = Field(
        ...,
        example="String type - this will contain more details about the problem encountered",
        description="Details about the problem encountered",
    )
