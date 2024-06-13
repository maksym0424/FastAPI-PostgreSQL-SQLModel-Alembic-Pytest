import pytest
from unittest.mock import patch
from master_server.database.user.model import User


@pytest.mark.anyio
@patch("master_server.database.user.service.UserService.update_user", return_value=True)
@patch("master_server.database.user.service.UserService.add_user", return_value=True)
@patch("master_server.utils.auth.AuthUtil.send_magic_link", return_value=True)
async def test_send_magic_link(
    mock_update_user, mock_add_user, mock_send_magic_link, test_client
):
    async def make_request_and_assert(email, expected_status, expected_response):
        response = await test_client.post(
            "/auth/send-magic-link", json={"email": email}
        )
        assert response.status_code == expected_status
        if expected_response:
            assert response.json() == expected_response

    # case 1: when user is fresh new
    with patch(
        "master_server.database.user.service.UserService.find_by_email",
        return_value=None,
    ):
        await make_request_and_assert("example@test.com", 200, True)

    # case 2: when user is already registered
    with patch(
        "master_server.database.user.service.UserService.find_by_email",
        return_value=User(email="example@test.com"),
    ):
        await make_request_and_assert("example@test.com", 200, True)

    # case 3: when user is banned
    with patch(
        "master_server.database.user.service.UserService.find_by_email",
        return_value=User(banned=True, email="example@test.com"),
    ):
        await make_request_and_assert(
            "example@test.com", 401, {"detail": "Banned user"}
        )

    # case 4: input invalid email
    with patch(
        "master_server.database.user.service.UserService.find_by_email",
        return_value=None,
    ):
        await make_request_and_assert("123", 422, None)


@pytest.mark.anyio
@patch("master_server.utils.auth.AuthUtil.create_jwt_token", return_value="jwttoken")
@patch(
    "master_server.database.user.service.UserService.update_user",
    return_value=User(id=1, email="example@test.com"),
)
async def test_verify_magic_link(mock_create_jwt_token, mock_update_user, test_client):
    async def make_request_and_assert(token, expected_status, expected_response):
        response = await test_client.get(f"/auth/verify-magic-link?token={token}")
        assert response.status_code == expected_status
        assert response.json() == expected_response

    # case 1: when token is not found
    with patch(
        "master_server.database.user.service.UserService.find_by_token",
        return_value=None,
    ):
        await make_request_and_assert("123456", 404, {"detail": "token not found"})

    # case 2: when token is found
    with patch(
        "master_server.database.user.service.UserService.find_by_token",
        return_value=User(id=1, email="example@test.com"),
    ):
        await make_request_and_assert(
            "123456", 200, {"token": "jwttoken", "user_id": 1}
        )
