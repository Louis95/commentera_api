"""
tests for user badges endpoints.
"""

import json

import pytest
from fastapi import HTTPException, status

from modules.database.models import Badge, User
from modules.database.schemas.user_schemas import AddBadges
from modules.routers.user import add_badges


class TestAddBadge:
    """
    Test cases for adding badges.
    """

    @staticmethod
    def test_add_badges_success(
        mocker,
        mock_add_badge_user,
        db_session,
        mock_customer_alias,
    ):
        """
        Test adding badges to a user successfully.
        """

        mocker.patch(
            "modules.actions.user.get_user_by_id_and_customer",
            return_value=mock_add_badge_user,
        )
        mocker.patch(
            "modules.utilities.auth.CUSTOMER_CONFIG.get_customer_config",
            return_value={"badges": ["PAID", "EDITOR"]},
        )

        response = add_badges(
            user_id=mock_add_badge_user.id,
            add_badge_info=AddBadges(badge_names=["PAID"]),
            customer_alias=mock_customer_alias,
            db_session=db_session,
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.message == "Add user badge request successful"

    @staticmethod
    def test_add_badges_invalid_badges(
        mocker,
        mock_add_badge_user,
        db_session,
        mock_customer_alias,
    ):
        """Test adding invalid badges"""

        mocker.patch(
            "modules.actions.user.get_user_by_id_and_customer",
            return_value=mock_add_badge_user,
        )
        mocker.patch(
            "modules.utilities.auth.CUSTOMER_CONFIG.get_customer_config",
            return_value={},
        )

        # Calling the endpoint
        with pytest.raises(HTTPException) as exc_info:
            add_badges(
                user_id=mock_add_badge_user.id,
                add_badge_info=AddBadges(badge_names=["badge2"]),
                customer_alias=mock_customer_alias,
                db_session=db_session,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert str(exc_info.value.detail) == "You have not configured badges yet"

    @staticmethod
    def test_add_badges_max_badges_exceeded(
        mocker,
        mock_add_badge_user,
        db_session,
        mock_customer_alias,
    ):
        """Test adding badges when max badge has been exceeded"""

        mocker.patch(
            "modules.actions.user.get_user_by_id_and_customer",
            return_value=mock_add_badge_user,
        )
        mocker.patch(
            "modules.utilities.auth.CUSTOMER_CONFIG.get_customer_config",
            return_value={"badges": ["EDITOR", "PAID"]},
        )
        mock_add_badge_user.badges = [Badge(badge_name="PAID")]

        with pytest.raises(HTTPException) as exc_info:
            add_badges(
                user_id=mock_add_badge_user.id,
                add_badge_info=AddBadges(badge_names=["EDITOR", "PAID"]),
                customer_alias=mock_customer_alias,
                db_session=db_session,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert str(exc_info.value.detail) == "Maximum 2 badges allowed per user"


class TestUpdateBadge:
    """
    Test cases for updating badges.
    """

    @staticmethod
    def test_successful_badge_update(
        client,
        generate_mock_token,
        mock_update_badge_user,
    ):
        """
        Test adding badges to a user successfully.
        """

        payload = {
            "old_badge_names": ["SPAMMER"],
            "new_badge_names": ["CONTRIBUTOR"],
        }
        response = client.patch(
            f"/users/{mock_update_badge_user.id}/badges/",
            json=payload,
            headers={"Authorization": generate_mock_token},
        )
        assert response.status_code == 200
        assert response.json() == {
            "status_code": 200,
            "message": "Update user badge request successful",
        }

    @staticmethod
    def test_mismatched_badge_count(
        db_session,
        client,
        generate_mock_token,
        mock_update_badge_user,
    ):
        """Test mismatched badge count"""

        payload = {
            "old_badge_names": ["badge1"],
            "new_badge_names": ["new_badge1", "new_badge2"],
        }
        response = client.patch(
            f"/users/{mock_update_badge_user.id}/badges/",
            json=payload,
            headers={"Authorization": generate_mock_token},
        )

        assert response.status_code == 422
        db_session.delete(mock_update_badge_user)
        db_session.commit()


class TestDeleteBadge:
    """
    Test cases for deleting badges.
    """

    @staticmethod
    def test_successful_badge_deletion(
        db_session,
        mock_delete_badge_user,
        generate_mock_token,
        client,
    ):
        """
        Test deleting user badges successfully.
        """
        payload = {
            "badge_names": ["CONTRIBUTOR"],
        }

        response = client.request(
            "DELETE",
            f"/users/{mock_delete_badge_user.id}/badges/",
            data=json.dumps(payload),
            headers={"Authorization": generate_mock_token},
        )

        assert response.status_code == 200
        assert response.json() == {
            "status_code": 200,
            "message": "Delete user badge request successful",
        }

        updated_user = db_session.query(User).get(mock_delete_badge_user.id)
        assert len(updated_user.badges) == 1
        assert updated_user.badges[0].badge_name == "SPAMMER"

        db_session.delete(updated_user)
        db_session.commit()
