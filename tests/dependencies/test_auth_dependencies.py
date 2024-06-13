import pytest
from datetime import datetime
from unittest.mock import patch
from master_server.database.user.model import User
from master_server.enums.user_enums import UserRoleEnum


@pytest.mark.anyio
async def test_ge_current_user(test_client):
    # case 1: when authentication token is not provided
    response = await test_client.get(
        "/user",
    )
    assert response.status_code == 403

    # case 2: when authentication token is invalid
    response = await test_client.get(
        "/user", headers={"Authorization": "bearer 123456"}
    )
    assert response.status_code == 401

    # case 3: when authentication token is valid, but user with that email not exist
    with patch(
        "master_server.utils.auth.AuthUtil.verify_jwt_token",
        return_value="example@test.com",
    ):
        with patch(
            "master_server.database.user.service.UserService.find_by_email",
            return_value=None,
        ):
            response = await test_client.get(
                "/user", headers={"Authorization": "bearer 123456"}
            )
            assert response.status_code == 404

    # case 4: when authentication token is valid and user exist, but banned
    with patch(
        "master_server.utils.auth.AuthUtil.verify_jwt_token",
        return_value="example@test.com",
    ):
        with patch(
            "master_server.database.user.service.UserService.find_by_email",
            return_value=User(id=1, email="example@test.com", banned=True),
        ):
            response = await test_client.get(
                "/user", headers={"Authorization": "bearer 123456"}
            )
            assert response.status_code == 401

    # case 5: when authentication token is valid and user exist, not banned
    with patch(
        "master_server.utils.auth.AuthUtil.verify_jwt_token",
        return_value="example@test.com",
    ):
        with patch(
            "master_server.database.user.service.UserService.find_by_email",
            return_value=User(id=1, email="example@test.com"),
        ):
            response = await test_client.get(
                "/user", headers={"Authorization": "bearer 123456"}
            )
            assert response.status_code == 200


@pytest.mark.anyio
async def test_get_active_user(test_client):
    # case 1: all user details not provided
    with patch(
        "master_server.utils.auth.AuthUtil.verify_jwt_token",
        return_value="example@test.com",
    ):
        with patch(
            "master_server.database.user.service.UserService.find_by_email",
            return_value=User(id=1, email="example@test.com"),
        ):
            response = await test_client.get(
                "/user/active-user", headers={"Authorization": "bearer 123456"}
            )
            assert response.status_code == 401

    # case 1: all user details are provided
    with patch(
        "master_server.utils.auth.AuthUtil.verify_jwt_token",
        return_value="example@test.com",
    ):
        with patch(
            "master_server.database.user.service.UserService.find_by_email",
            return_value=User(
                id=1,
                username="testuser",
                first_name="Jane",
                last_name="Doe",
                date_of_birth=datetime(1990, 1, 1),
                address={"city": "Test City", "street": "123 Main St"},
                phone={"home": "123-555-5555"},
                email="jane.doe@example.com",
                created_with_ip="192.0.2.1",
                last_login_with_ip="192.0.2.1",
                profile_pic_url="https://example.com/profile.jpg",
                banned=False,
                role=UserRoleEnum.USER,
                balance=100,
                referral_code="ABCDE",
                api_key="A1B2C3D4E5F6G7H8I9J0",
                is_verified=True,
            ),
        ):
            response = await test_client.get(
                "/user/active-user", headers={"Authorization": "bearer 123456"}
            )
            assert response.status_code == 200
