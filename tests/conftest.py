"""Conftest file"""
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from main import app
from modules.database.models import Badge, User
from modules.utilities.auth import SECRET_KEY
from modules.utilities.database import SessionLocal


@pytest.fixture(scope="module")
def client():
    """
    Create a FastAPI test client using the app fixture.
    """
    return TestClient(app=app)


@pytest.fixture
def mock_get():
    """Mock get request"""
    with patch("requests.get") as mock:
        yield mock


@pytest.fixture
def mock_redis():
    """Mock redis"""
    with patch("redis.Redis") as mock:
        yield mock.return_value


@pytest.fixture
def db_session():
    """
    Create a new database session for each test.
    """
    test_db_session = SessionLocal()
    yield test_db_session
    test_db_session.close()


@pytest.fixture
def mock_generate_jwt_token(mocker: MockerFixture):
    """
    Mock the generate_jwt_token function.
    """
    return mocker.patch(
        "modules.utilities.auth.generate_jwt_token",
        return_value="mocked_token",
    )


@pytest.fixture
def mock_customer_alias():
    """Test customer alias"""
    return "bbg"


@pytest.fixture
# pylint: disable=W0621
def mock_add_badge_user(db_session):
    """Create mock user for adding badges"""

    new_test_user = User(id=uuid4(), customer_id="bbg")
    db_session.add(new_test_user)
    db_session.commit()

    return new_test_user


@pytest.fixture
# pylint: disable=W0621
def mock_update_badge_user(db_session):
    """Create mock user for updating badges"""

    mock_user = User(id=uuid4(), customer_id="xbahn")
    badge1 = Badge(badge_name="SPAMMER", user=mock_user)
    db_session.add(mock_user)
    db_session.add_all([badge1])
    db_session.commit()
    return mock_user


@pytest.fixture
# pylint: disable=W0621
def mock_delete_badge_user(db_session):
    """Create mock user for deleting badges"""
    mock_user = User(id=uuid4(), customer_id="xbahn")
    badge1 = Badge(badge_name="SPAMMER", user=mock_user)
    badge2 = Badge(badge_name="CONTRIBUTOR", user=mock_user)

    db_session.add(mock_user)
    db_session.add_all([badge1, badge2])
    db_session.commit()
    return mock_user


@pytest.fixture
def generate_mock_token():
    """Generate test token"""
    token_payload = {
        "customer_alias": "xbahn",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    test_token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
    return f"Bearer {test_token}"
