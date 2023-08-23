"""
Tests for user badges endpoints.

"""
from fastapi import HTTPException, status


def test_generate_token_valid_customer(client):
    """
    Test generating a token for a valid and active customer.
    """
    response = client.post(
        "/generate_token",
        json={"customer_alias": "bbg"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token"]


def test_generate_token_invalid_customer(client, mock_generate_jwt_token):
    """
    Test generating a token for an invalid customer.
    """
    mock_generate_jwt_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid customer alias",
    )
    response = client.post(
        "/generate_token",
        json={"customer_alias": "invalid_customer"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unregistered customer"}


def test_generate_token_inactive_customer(client, mock_generate_jwt_token):
    """
    Test generating a token for an inactive customer.
    """
    mock_generate_jwt_token.side_effect = HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail="Payment required",
    )
    response = client.post(
        "/generate_token",
        json={"customer_alias": "airhansa"},
    )
    print(response.status_code)
    assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
    assert response.json() == {"detail": "Payment required"}
