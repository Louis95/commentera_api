import logging
from fastapi import HTTPException, status, APIRouter, Body
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
        customer_alias_info: GenerateToken = Body(..., description='Customer alias'),
) -> dict[str, str]:
    """
    Generate a token for the specified customer alias.

    Args:
        customer_alias_info (GenerateToken): Customer alias information.

    Returns:
        dict: Generated token.

    Raises:
        HTTPException: If unable to generate the token.
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
