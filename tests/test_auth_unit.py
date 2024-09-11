import pytest
import time
from unittest.mock import AsyncMock, MagicMock
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import (
    get_password_hash,
    create_user, authenticate_user, refresh_user_token
)
from src.auth.models import User
from src.auth.schemas import CreateUserReq

SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_create_user():
    db_mock = AsyncMock(AsyncSession)
    user_data = CreateUserReq(email="test@example.com", name="Test", password="password123")

    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    user = await create_user(user_data, db_mock)

    assert user.email == "test@example.com"
    assert db_mock.add.called
    assert db_mock.commit.called
    assert db_mock.refresh.called


@pytest.mark.asyncio
async def test_authenticate_user_success():
    db_mock = AsyncMock(AsyncSession)
    hashed_password = get_password_hash("password123")
    test_user = User(email="test@example.com", hashed_password=hashed_password, last_login=int(time.time()))

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = test_user
    db_mock.execute.return_value = result_mock

    user = await authenticate_user("test@example.com", "password123", db_mock)

    assert user is not None
    assert user.email == "test@example.com"
    assert db_mock.commit.called


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    db_mock = AsyncMock(AsyncSession)
    hashed_password = get_password_hash("password123")
    test_user = User(email="test@example.com", hashed_password=hashed_password, last_login=int(time.time()))

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = test_user
    db_mock.execute.return_value = result_mock

    user = await authenticate_user("test@example.com", "wrongpassword", db_mock)

    assert user is False
    assert not db_mock.commit.called


@pytest.mark.asyncio
async def test_refresh_user_token_invalid():
    db_mock = AsyncMock(AsyncSession)

    token = "invalid_token"

    with pytest.raises(Exception):  # credentials_exception будет выброшено
        await refresh_user_token(token, db_mock)

    assert not db_mock.commit.called
