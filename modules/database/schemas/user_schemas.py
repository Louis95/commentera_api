"""Schemas for various badge operations"""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class UpdateBadges(BaseModel):
    """Update Badges schema"""

    new_badge_names: List[str] = Field(
        ...,
        description="List of new badges to be assigned to the user",
        max_length=2,
        min_length=1,
    )
    old_badge_names: List[str] = Field(
        ...,
        description="List of badges to be updated",
        max_length=2,
        min_length=1,
    )

    @model_validator(mode="before")
    # pylint: disable=E0213
    def validate_number_of_badges_to_update(
        cls,
        values,
    ):
        """Validate the number of badges to be updated

        :param values: schema values
        :return: schema values
        """
        new_badges = values.get("new_badge_names")
        old_badges = values.get("old_badge_names")
        if len(new_badges) != len(old_badges):
            raise ValueError("Number of new badges must match the number of old badges")

        return values


class AddBadges(BaseModel):
    """Add badges schema"""

    badge_names: List[str] = Field(
        ...,
        description="List of badges to be added to the user",
        max_length=2,
        min_length=1,
    )


class DeleteBadges(BaseModel):
    """Delete badges schema"""

    badge_names: List[str] = Field(
        ...,
        description="List of badges to be deleted to the user",
        max_length=2,
        min_length=1,
    )


class BadgeSchema(BaseModel):
    """Badge schema"""

    badge_name: str = Field(None, description="Badge name")


class UserSchema(BaseModel):
    """User schema"""

    id: UUID = Field(None, description="user id")
    customer_alias: str = Field(None, description="Customer alias")
    badges: List[BadgeSchema]

    class ConfigDict:
        """Configuration for this schema class"""

        from_attributes = True
