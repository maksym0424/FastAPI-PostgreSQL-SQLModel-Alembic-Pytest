import pytest
from pydantic import ValidationError
from master_server.database.user.model import User


def test_user_model():
    # Valid user creation
    try:
        valid_user = User.model_validate(
            {
                "username": "valid_user",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
                "referral_code": "ABCDE",
                "api_key": "123456789012345678901234567890",
                "balance": 100,
            }
        )
    except ValidationError as e:
        pytest.fail(f"Valid user creation failed: {e}")

    # Invalid referral code
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid_user",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
                "referral_code": "ABC!",
            }
        )

    # Invalid token
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid_user",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
                "token": "ABC!",
            }
        )

    # Invalid api_key
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid_user_1",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
                "api_key": "123",
            }
        )

    # Email exceeding length
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid_user_2",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "a" * 257 + "@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # Invalid email format
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid_user_3",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # Username exceeding length
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "x" * 31,
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # Username with invalid characters
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "invalid user",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # First name exceeding length
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "valid_user",
                "first_name": "x" * 51,
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # Last name exceeding length
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "valid_user",
                "first_name": "Jane",
                "last_name": "x" * 51,
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # IP address exceeding length
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "valid_user",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "x" * 46,
                "last_login_with_ip": "203.0.113.195",
            }
        )

    # Negative balance
    with pytest.raises(ValidationError) as excinfo:
        User.model_validate(
            {
                "username": "valid_user",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "created_with_ip": "203.0.113.195",
                "last_login_with_ip": "203.0.113.195",
                "balance": -5,
            }
        )
