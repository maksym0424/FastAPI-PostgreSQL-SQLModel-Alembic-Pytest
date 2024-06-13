import pytest
from pydantic import ValidationError
from unittest.mock import patch
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from master_server.database.user.model import User
from master_server.database.user.service import UserService
from master_server.database.user.exception import (
    EmailAlreadyTaken,
    UsernameAlreadyTaken,
)


@pytest.fixture(name="user_service")
def user_service_fixture(session):
    return UserService(db_session=session)


@pytest.mark.anyio
async def test_add_user(user_service: UserService, session: AsyncSession):
    # Create a new user
    user = User(username="testuser", email="testuser@example.com")

    # case 1: valid user add
    with patch.object(
        user_service, "is_username_exist", return_value=False
    ), patch.object(user_service, "is_email_exist", return_value=False):
        # Add the user
        added_user = await user_service.add_user(user)

        # Verify the user was added
        assert added_user.id is not None  # ID should be set by the database
        assert added_user.username == "testuser"
        assert added_user.email == "testuser@example.com"

        # Verify the user was actually committed to the database
        statement = select(User).where(User.id == added_user.id)
        results = await session.exec(statement)
        db_user = results.one()

        assert db_user.id == added_user.id
        assert db_user.username == "testuser"
        assert db_user.email == "testuser@example.com"

    # case 2: username already exist
    with patch.object(
        user_service, "is_username_exist", return_value=True
    ), patch.object(user_service, "is_email_exist", return_value=False):
        with pytest.raises(UsernameAlreadyTaken):
            await user_service.add_user(user)

    # case 3: email already exist
    with patch.object(
        user_service, "is_username_exist", return_value=False
    ), patch.object(user_service, "is_email_exist", return_value=True):
        with pytest.raises(EmailAlreadyTaken):
            await user_service.add_user(user)


# Test for update_user method
@pytest.mark.anyio
async def test_update_user(user_service: UserService, session: AsyncSession):
    # Create a new user
    user = User(username="testuser", email="testuser@example.com")

    # Save the user to the database
    session.add(user)
    await session.commit()
    await session.refresh(user)

    updated_username = "updateduser"
    updated_email = "updateduser@example.com"

    # case 1: valid user update
    with patch.object(
        user_service, "is_username_exist", return_value=False
    ), patch.object(user_service, "is_email_exist", return_value=False):
        updated_user = await user_service.update_user(
            user, username=updated_username, email=updated_email
        )

        assert updated_user.username == updated_username
        assert updated_user.email == updated_email

    # case 2: username already exist
    with patch.object(
        user_service, "is_username_exist", return_value=True
    ), patch.object(user_service, "is_email_exist", return_value=False):
        with pytest.raises(UsernameAlreadyTaken):
            await user_service.update_user(
                user, username=updated_username, email=updated_email
            )

    # case 3: email already exist
    with patch.object(
        user_service, "is_username_exist", return_value=False
    ), patch.object(user_service, "is_email_exist", return_value=True):
        with pytest.raises(EmailAlreadyTaken):
            await user_service.update_user(
                user, username=updated_username, email=updated_email
            )

    # case 4: invalid model update
    with patch.object(
        user_service, "is_username_exist", return_value=False
    ), patch.object(user_service, "is_email_exist", return_value=False):
        with pytest.raises(ValueError):
            await user_service.update_user(user, api_key="not 30 length")


# Test for finding a user by api_key
@pytest.mark.anyio
async def test_find_by_api_key(user_service: UserService, session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com", api_key="apikey123")

    # Save the user to the database
    session.add(user)
    await session.commit()
    await session.refresh(user)

    result = await user_service.find_by_api_key("apikey123")
    assert result == user

    result = await user_service.find_by_api_key("not_existing")
    assert result == None


# Test for finding a user by token
@pytest.mark.anyio
async def test_find_by_token(user_service: UserService, session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com")

    # Save the user to the database
    session.add(user)
    await session.commit()
    await session.refresh(user)

    result = await user_service.find_by_token(user.token)
    assert result == user

    result = await user_service.find_by_token("not_existing")
    assert result == None


# Test for finding a user by email
@pytest.mark.anyio
async def test_find_by_email(user_service: UserService, session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com")

    session.add(user)
    await session.commit()
    await session.refresh(user)

    result = await user_service.find_by_email("testuser@example.com")
    assert result == user

    result = await user_service.find_by_email("notexsting@example.com")
    assert result == None


# Test for is_username_exist method
@pytest.mark.anyio
async def test_is_username_exist(user_service: UserService, session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com")

    session.add(user)
    await session.commit()
    await session.refresh(user)

    result = await user_service.is_username_exist("testuser")
    assert result is True

    result = await user_service.is_username_exist("non_existent_user")
    assert result is False


# Test for is_email_exist method
@pytest.mark.anyio
async def test_is_email_exist(user_service: UserService, session: AsyncSession):
    user = User(username="testuser", email="testuser@example.com")

    session.add(user)
    await session.commit()
    await session.refresh(user)

    result = await user_service.is_email_exist("testuser@example.com")
    assert result is True

    result = await user_service.is_email_exist("non_existent_email@example.com")
    assert result is False
