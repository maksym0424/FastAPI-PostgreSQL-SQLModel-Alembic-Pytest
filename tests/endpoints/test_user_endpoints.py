import pytest
from unittest.mock import patch
from master_server.database.user.model import User
from master_server.database.user.exception import (
    UsernameAlreadyTaken,
    EmailAlreadyTaken,
)
from master_server.server import app


@pytest.mark.anyio
async def test_patch_user(test_client, override_dependencies):
    # case 1: username already taken
    with patch(
        "master_server.database.user.service.UserService.update_user",
        side_effect=UsernameAlreadyTaken,
    ):
        response = await test_client.patch(
            "/user",
            headers={"Authorization": "bearer 123456"},
            json={"username": "test"},
        )
        assert response.status_code == 400

    # case 2: email already taken
    with patch(
        "master_server.database.user.service.UserService.update_user",
        side_effect=EmailAlreadyTaken,
    ):
        response = await test_client.patch(
            "/user",
            headers={"Authorization": "bearer 123456"},
            json={"email": "example@test.com"},
        )
        assert response.status_code == 400

    # case 3: valid request
    with patch(
        "master_server.database.user.service.UserService.update_user",
        return_value=User(id=1, email="example@test.com"),
    ):
        response = await test_client.patch(
            "/user",
            headers={"Authorization": "bearer 123456"},
            json={"email": "example@test.com"},
        )
        assert response.status_code == 200

    # case 4: forbidden fields testing
    with patch(
        "master_server.database.user.service.UserService.update_user",
        return_value=User(id=1, email="example@test.com"),
    ):
        response = await test_client.patch(
            "/user",
            headers={"Authorization": "bearer 123456"},
            json={"is_verified": True},
        )
        assert response.status_code == 422
