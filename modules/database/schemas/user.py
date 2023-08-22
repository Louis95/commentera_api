"""Schemas for various badge operations"""


from typing import List

from pydantic import BaseModel, Field


class UpdateBadges(BaseModel):
    """Update Badges schema"""

    badge_names: List[str] = Field(
        ...,
        description="List of badges to update to the user",
        max_items=2,
        min_items=1,
    )


class AddBadges(BaseModel):
    """Add badges schema"""

    badge_names: List[str] = Field(
        ...,
        description="List of badges to be added to the user",
        max_items=2,
        min_items=1,
    )


class DeleteBadges(BaseModel):
    """Delete badges schema"""

    badge_names: List[str] = Field(
        ...,
        description="List of badges to be deleted to the user",
        max_items=2,
        min_items=1,
    )
