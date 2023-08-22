"""
Authentication Utilities
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
import os

from modules.utilities.config import app_config
from modules.actions.customer import CustomerConfig
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

security = HTTPBearer()

SECRET_KEY = app_config.secret_key

load_dotenv()

CUSTOMER_CONFIG = CustomerConfig(
    redis_host=os.getenv("REDIS_HOST"),
    redis_port=int(os.getenv("REDIS_PORT")),
    refresh_rate=int(os.getenv("REFRESH_RATE", 300))
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="generate_token", auto_error=False, description="Bearer token for authentication"
)


def authenticate_customer(bearer_token: str = Depends(oauth2_scheme)) -> str:
    """
    Authenticate a customer based on bearer token.

    Args:
        bearer_token (str): Bearer token.

    Returns:
        str: Customer alias.

    Raises:
        HTTPException: If authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if bearer_token is None:
            raise credentials_exception

        payload = jwt.decode(bearer_token, SECRET_KEY, algorithms=["HS256"])
        customer_alias = payload.get("customer_alias")

        customer_info = CUSTOMER_CONFIG.get_customer_config(customer_alias)
        if not customer_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unregistered customer",
            )

        customer_status = customer_info.get("status")
        if customer_status != "active":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment required",
            )

        return customer_alias
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )


def generate_jwt_token(customer_alias: str) -> str:
    """
    Generate JWT token for a customer alias.

    Args:
        customer_alias (str): Customer alias.

    Returns:
        str: JWT token.
    """
    payload = {
        "customer_alias": customer_alias,
        "exp": datetime.utcnow() + timedelta(minutes=30)  # Token expiration time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def generate_customer_token(customer_alias: str) -> dict:
    """
    Generate JWT token for a customer alias.

    Args:
        customer_alias (str): Customer alias.

    Returns:
        dict: Token response.

    Raises:
        HTTPException: If customer alias is invalid or not active.
    """
    customer_config = CUSTOMER_CONFIG.get_customer_config(customer_alias)
    if not customer_config:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid customer alias",
        )

    customer_status = customer_config.get('status')
    if customer_status != "active":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required",
        )

    # Generate and return the JWT token
    token = generate_jwt_token(customer_alias)
    return {"token": token}
