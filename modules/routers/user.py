"""User related routers"""
import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security, status
from sqlalchemy.orm import Session

from modules.actions.user import (
    add_badges_to_user,
    delete_user_badges,
    get_user_by_id_and_customer,
    update_user_badges,
)
from modules.database.schemas.user import AddBadges, DeleteBadges, UpdateBadges
from modules.utilities.auth import authenticate_customer
from modules.utilities.database import get_db_session
from modules.utilities.response import base_responses

router = APIRouter(
    tags=["User"],
    responses={**base_responses},
)
logger = logging.getLogger(__name__)


@router.post("/users/{user_id}/badges/")
async def add_badges(
    user_id: UUID = Path(..., description="The Id of the user to update badges for"),
    add_badge_info: AddBadges = Body(..., description="List of badges to be added"),
    customer_alias: str = Security(authenticate_customer),
    db_session: Session = Depends(get_db_session),
) -> dict:
    """
    Add badges to a user.

    Args:
        user_id (UUID): The ID of the user.
        add_badge_info (AddBadges): List of badges to be added.
        customer_alias (str): Customer alias obtained from authentication.
        db_session (Session): SQLAlchemy session.

    Returns:
        dict: Response message.

    Raises:
        HTTPException: If unable to add badges.
    """
    try:
        user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

        # Check if the user has configured badges
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with user id: {user_id}",
            )

        return add_badges_to_user(user, add_badge_info, db_session)

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception


@router.patch("/users/{user_id}/badges/")
async def update_badges(
    user_id: UUID = Path(..., description="The Id of the user to update badges for"),
    update_badge_info: UpdateBadges = Body(
        ...,
        description="List of badges to be updated.",
    ),
    db_session: Session = Depends(get_db_session),
    customer_alias: str = Depends(authenticate_customer),
) -> dict:
    """
    Update badges for a user.

    Args:
        user_id (UUID): The ID of the user.
        update_badge_info (UpdateBadges): List of badges to be updated.
        db_session (Session): SQLAlchemy session.
        customer_alias (str): Customer alias obtained from authentication.

    Returns:
        dict: Response message.

    Raises:
        HTTPException: If unable to update badges.
    """
    try:
        user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

        # Check if the user has configured badges
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with user id: {user_id}",
            )

        return update_user_badges(user, update_badge_info, db_session)

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception


@router.delete("/users/{user_id}/badges/")
async def delete_badges(
    user_id: UUID = Path(..., description="The Id of the user to delete badges for"),
    delete_badge_info: DeleteBadges = Body(
        ...,
        description="List of badges to be deleted.",
    ),
    db_session: Session = Depends(get_db_session),
    customer_alias: str = Depends(authenticate_customer),
) -> dict:
    """
    Delete badges from a user.

    Args:
        user_id (UUID): The ID of the user.
        delete_badge_info (DeleteBadges): List of badges to be deleted.
        db_session (Session): SQLAlchemy session.
        customer_alias (str): Customer alias obtained from authentication.

    Returns:
        dict: Response message.

    Raises:
        HTTPException: If unable to delete badges.
    """
    user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

    try:
        return delete_user_badges(user, delete_badge_info, db_session)

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception
