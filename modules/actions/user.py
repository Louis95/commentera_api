"""User related actions"""
from typing import List
from uuid import UUID

import sqlalchemy
import sqlalchemy.exc
from fastapi import HTTPException, status
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from modules.database.models import Badge, User
from modules.database.schemas.user_schemas import (
    AddBadges,
    BadgeSchema,
    DeleteBadges,
    UpdateBadges,
    UserSchema,
)
from modules.utilities.auth import CUSTOMER_CONFIG


def get_user_by_id_and_customer(
    user_id: UUID,
    customer_alias: str,
    db_session: Session,
) -> User:
    """
    Get a user by ID and customer alias.

    :param user_id: User ID.
    :param customer_alias: Customer alias.
    :param db_session: Database session.
    :return: User object.
    :raises HTTPException: If user not found.
    """
    try:
        return (
            db_session.query(User)
            .filter(
                User.id == user_id,
                cast(User.customer_id, String) == customer_alias,
            )
            .first()
        )
    except sqlalchemy.exc.NoResultFound as no_result_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with user id: {user_id}",
        ) from no_result_exception


def add_badges_to_user(
    user: User,
    add_badge_info: AddBadges,
    db_session: Session,
) -> None:
    """
    Add badges to a user.

    :param user: User object.
    :param add_badge_info: Badge information to add.
    :param db_session: Database session.
    :return: None.
    """
    customer_info = CUSTOMER_CONFIG.get_customer_config(user.customer_id)

    if not customer_info.get("badges"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not configured badges yet",
        )

    if not CUSTOMER_CONFIG.is_valid_customer_badges(
        user.customer_id,
        add_badge_info.badge_names,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have all the badge(s) provided in the request",
        )

    if len(user.badges) + len(add_badge_info.badge_names) > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 2 badges allowed per user",
        )

    for badge_name in add_badge_info.badge_names:
        badge = Badge(badge_name=badge_name, user=user)
        db_session.add(badge)

    db_session.commit()


def update_user_badges(
    user: User,
    update_badge_info: UpdateBadges,
    db_session: Session,
) -> None:
    """
    Update user badges.

    :param user: User object.
    :param update_badge_info: Badge information to update.
    :param db_session: Database session.
    :return: None.
    """
    customer_info = CUSTOMER_CONFIG.get_customer_config(user.customer_id)
    if not customer_info.get("badges"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not configured badges yet",
        )

    if not CUSTOMER_CONFIG.is_valid_customer_badges(
        user.customer_id,
        update_badge_info.new_badge_names,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have all the badge(s) provided in the request",
        )
    old_badge_names = update_badge_info.old_badge_names
    new_badge_names = update_badge_info.new_badge_names

    if len(old_badge_names) != len(new_badge_names):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of old and new badges must be the same",
        )

    user_badge_names = [badge.badge_name for badge in user.badges]

    # Check if the user has all the old badges
    if not all(
        old_badge_name in user_badge_names for old_badge_name in old_badge_names
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have all the old badges to be updated",
        )

    # Update the badges
    for badge, new_badge_name in zip(user.badges, new_badge_names):
        badge_index = user_badge_names.index(badge.badge_name)
        user.badges[badge_index].badge_name = new_badge_name

    db_session.commit()


def delete_user_badges(
    user: User,
    delete_badge_info: DeleteBadges,
    db_session: Session,
) -> None:
    """
    Delete user badges.

    :param user: User object.
    :param delete_badge_info: Badge information to delete.
    :param db_session: Database session.
    :return: Response message.
    """
    for badge_name in delete_badge_info.badge_names:
        badge = (
            db_session.query(Badge)
            .filter_by(user_id=user.id, badge_name=badge_name)
            .first()
        )
        if badge:
            db_session.delete(badge)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Badge '{badge_name}' does not exist for the user",
            )

    db_session.commit()


def get_customer_users(customer_alias: str, db_session: Session) -> List[UserSchema]:
    """
    Get users by customer ID.

    :param customer_alias: customer alias.
    :param db_session: Database session.
    :return: Response message.
    """

    users: List[User] = (
        db_session.query(User).filter_by(customer_id=customer_alias).all()
    )
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No users found for customer_id: {customer_alias}",
        )

    # Convert User objects to UserSchema objects
    user_schemas = []
    for user in users:
        badge_schemas = [
            BadgeSchema(badge_name=badge.badge_name) for badge in user.badges
        ]
        user_schema = UserSchema(
            id=user.id,
            customer_alias=user.customer_id,
            badges=badge_schemas,
        )
        user_schemas.append(user_schema)

    return user_schemas
