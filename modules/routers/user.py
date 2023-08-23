"""User related routers"""
import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Security, status
from sqlalchemy.orm import Session

from modules.actions.user import (
    add_badges_to_user,
    delete_user_badges,
    get_customer_users,
    get_user_by_id_and_customer,
    update_user_badges,
)
from modules.database.schemas.user import (
    AddBadges,
    DeleteBadges,
    UpdateBadges,
    UserSchema,
)
from modules.database.schemas.utility_schemas import SuccessfulResponseOut
from modules.utilities.auth import authenticate_customer
from modules.utilities.database import get_db_session
from modules.utilities.response import base_responses

router = APIRouter(
    tags=["User"],
    responses={**base_responses},
)
logger = logging.getLogger(__name__)


@router.post("/users/{user_id}/badges/", response_model=SuccessfulResponseOut)
def add_badges(
    user_id: UUID = Path(..., description="The Id of the user to update badges for"),
    add_badge_info: AddBadges = Body(..., description="List of badges to be added"),
    customer_alias: str = Security(authenticate_customer),
    db_session: Session = Depends(get_db_session),
) -> SuccessfulResponseOut:
    """
    Add badges to a user.
    """
    try:
        user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

        # Check if the user has configured badges
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with user id: {user_id}",
            )
        add_badges_to_user(user, add_badge_info, db_session)
        return SuccessfulResponseOut(
            status_code=status.HTTP_200_OK,
            message="Add user badge request successful",
        )

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception


@router.patch("/users/{user_id}/badges/", response_model=SuccessfulResponseOut)
def update_badges(
    user_id: UUID = Path(..., description="The Id of the user to update badges for"),
    update_badge_info: UpdateBadges = Body(
        ...,
        description="List of badges to be updated.",
    ),
    db_session: Session = Depends(get_db_session),
    customer_alias: str = Depends(authenticate_customer),
) -> SuccessfulResponseOut:
    """
    Update badges for a user.
    """
    try:
        user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

        # Check if the user has configured badges
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with user id: {user_id}",
            )

        update_user_badges(user, update_badge_info, db_session)
        return SuccessfulResponseOut(
            status_code=status.HTTP_200_OK,
            message="Update user badge request successful",
        )

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception


@router.delete("/users/{user_id}/badges/", response_model=SuccessfulResponseOut)
def delete_badges(
    user_id: UUID = Path(..., description="The Id of the user to delete badges for"),
    delete_badge_info: DeleteBadges = Body(
        ...,
        description="List of badges to be deleted.",
    ),
    db_session: Session = Depends(get_db_session),
    customer_alias: str = Depends(authenticate_customer),
) -> SuccessfulResponseOut:
    """
    Delete badges from a user.
    """
    user = get_user_by_id_and_customer(user_id, customer_alias, db_session)

    try:
        delete_user_badges(user, delete_badge_info, db_session)
        return SuccessfulResponseOut(
            status_code=status.HTTP_200_OK,
            message="Delete user badge request successful",
        )

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to add new badge: {str(general_exception)}",
        ) from general_exception


@router.get("/users/by_customer/", response_model=List[UserSchema])
def get_users_by_customer_id(
    db_session: Session = Depends(get_db_session),
    customer_alias: str = Depends(authenticate_customer),
) -> List[UserSchema]:
    """
    Retrieve a list of users with a specific customer_id.

    This endpoint allows you to retrieve all users associated with a given customer_id.

    """
    try:
        return get_customer_users(customer_alias, db_session)

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to get users: {str(general_exception)}",
        ) from general_exception
