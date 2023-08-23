"""Auth related routers"""
import logging

from fastapi import APIRouter, Body, HTTPException, status

from modules.database.schemas.auth_schema import GenerateToken
from modules.utilities.auth import generate_customer_token
from modules.utilities.response import base_responses

router = APIRouter(
    tags=["Auth"],
    responses={**base_responses},
)
logger = logging.getLogger(__name__)


@router.post("/generate_token")
def generate_token(
    customer_alias_info: GenerateToken = Body(..., description="Customer alias"),
) -> dict[str, str]:
    """
    Generate a token for the specified customer alias.
    """
    try:
        return generate_customer_token(customer_alias_info.customer_alias)

    except Exception as general_exception:
        if isinstance(general_exception, HTTPException):
            raise general_exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate Token: {str(general_exception)}",
        ) from general_exception
