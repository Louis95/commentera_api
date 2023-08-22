"""User related actions"""
from uuid import UUID

import sqlalchemy
import sqlalchemy.exc
from fastapi import HTTPException, status
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from modules.database.models import Badge, User
from modules.database.schemas.user import AddBadges, DeleteBadges, UpdateBadges
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
) -> dict:
    """
    Add badges to a user.

    :param user: User object.
    :param add_badge_info: Badge information to add.
    :param db_session: Database session.
    :return: Response message.
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
    return {"message": "Badges added successfully"}


def update_user_badges(
    user: User,
    update_badge_info: UpdateBadges,
    db_session: Session,
) -> dict:
    """
    Update user badges.

    :param user: User object.
    :param update_badge_info: Badge information to update.
    :param db_session: Database session.
    :return: Response message.
    """
    customer_info = CUSTOMER_CONFIG.get_customer_config(user.customer_id)

    if not customer_info.get("badges"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not configured badges yet",
        )

    if not CUSTOMER_CONFIG.is_valid_customer_badges(
        user.customer_id,
        update_badge_info.badge_names,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not have all the badge(s) provided in the request",
        )

    num_user_badges = len(user.badges)
    num_request_badges = len(update_badge_info.badge_names)

    if num_user_badges == 2 and num_request_badges == 1:
        user.badges[0].badge_name = update_badge_info.badge_names[0]
    elif num_user_badges == 1 and num_request_badges == 1:
        new_badge = Badge(badge_name=update_badge_info.badge_names[0], user=user)
        db_session.add(new_badge)
    elif num_request_badges == 2:
        for badge, new_badge_name in zip(user.badges, update_badge_info.badge_names):
            badge.badge_name = new_badge_name

    db_session.commit()
    return {"message": "Badges updated successfully"}


def delete_user_badges(
    user: User,
    delete_badge_info: DeleteBadges,
    db_session: Session,
) -> dict:
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

    db_session.commit()
    return {"message": "Badges deleted successfully"}
