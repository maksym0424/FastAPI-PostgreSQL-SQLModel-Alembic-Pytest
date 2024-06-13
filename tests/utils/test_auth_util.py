import string
import pytest
import hashlib
from jose import JWTError
from unittest.mock import patch, ANY, MagicMock
from urllib.parse import urlencode
from master_server.utils.auth import AuthUtil
from master_server.config import get_settings


@pytest.fixture(name="auth_util")
def auth_util_fixture(session):
    return AuthUtil()


# Test for JWT Token creation
def test_create_jwt_token(auth_util: AuthUtil):
    email = "test@example.com"

    with patch("jose.jwt.encode", return_value="mock_token") as mock_encode:
        token = auth_util.create_jwt_token(email)

        assert token == "mock_token"
        mock_encode.assert_called_once_with(
            {"sub": email, "exp": ANY},
            auth_util.settings.JWT_SECRET_KEY,
            algorithm=auth_util.settings.JWT_ALGORITHM,
        )


# Test for JWT Token verification
def test_verify_jwt_token(auth_util: AuthUtil):
    email = "test@example.com"

    # case 1: verify_jwt_token success
    with patch("jose.jwt.decode", return_value={"sub": email}) as mock_decode:
        token = auth_util.create_jwt_token(email)
        extracted_email = auth_util.verify_jwt_token(token)

        assert extracted_email == email
        mock_decode.assert_called_once_with(
            token,
            auth_util.settings.JWT_SECRET_KEY,
            algorithms=[auth_util.settings.JWT_ALGORITHM],
        )

    # case 1: verify_jwt_token failed with JWTError
    with patch("jose.jwt.decode", side_effect=JWTError):
        extracted_email = auth_util.verify_jwt_token("invalid_token")

        assert extracted_email is None


# Test for sending magic link
def test_send_magic_link(auth_util: AuthUtil):
    # case 1: SendGridAPIClient.send success
    with patch("master_server.utils.auth.SendGridAPIClient") as mock_sendgrid:
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_sendgrid.return_value.send.return_value = mock_response

        success = auth_util.send_magic_link(
            "http://example.com", "test@example.com", "token123"
        )

        assert success is True
        mock_sendgrid.assert_called_once_with(auth_util.settings.SENDGRID_API_KEY)

    # case 2: SendGridAPIClient.send failed with 400 error
    with patch("master_server.utils.auth.SendGridAPIClient") as mock_sendgrid:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_sendgrid.return_value.send.return_value = mock_response

        success = auth_util.send_magic_link(
            "http://example.com", "test@example.com", "token123"
        )

        assert success is False
        mock_sendgrid.assert_called_once_with(auth_util.settings.SENDGRID_API_KEY)

    # case 3: SendGridAPIClient.send failed with SendGrid exception
    with patch(
        "master_server.utils.auth.SendGridAPIClient",
        side_effect=Exception("SendGrid error"),
    ):
        success = auth_util.send_magic_link(
            "http://example.com", "test@example.com", "token123"
        )

        assert success is False


# Test for generate_referral_code method
def test_generate_referral_code(auth_util: AuthUtil):
    referral_code = auth_util.generate_referral_code()
    assert len(referral_code) == 5
    assert all(c in string.ascii_letters + string.digits for c in referral_code)


# Test for generate_login_token method
def test_generate_login_token(auth_util: AuthUtil):
    api_key = auth_util.generate_login_token()
    assert len(api_key) == 20
    assert all(c in string.ascii_letters + string.digits for c in api_key)


# Test for get_user_gravatar_url method
def test_get_user_gravatar_url():
    auth_util = AuthUtil()
    email = "test@example.com"
    expected_email_hash = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
    default_img = "identicon"
    size = 40

    def mocked_urlencode(query):
        return urlencode(query)

    with patch("hashlib.md5") as mock_md5, patch(
        "urllib.parse.urlencode", side_effect=mocked_urlencode
    ) as mock_urlencode:
        mocked_md5_instance = mock_md5.return_value
        mocked_md5_instance.hexdigest.return_value = expected_email_hash

        # case 1: get_user_gravatar_url success
        gravatar_url = auth_util.get_user_gravatar_url(email)
        expected_query_params = mocked_urlencode({"d": default_img, "s": str(size)})
        expected_url = f"https://www.gravatar.com/avatar/{expected_email_hash}?{expected_query_params}"
        assert gravatar_url == expected_url

        # Reset mocks for the next test cases
        mock_md5.reset_mock()
        mock_urlencode.reset_mock()

        # case 2: get_user_gravatar_url with empty email
        email_empty = ""
        empty_email_hash = hashlib.md5(email_empty.encode("utf-8")).hexdigest()
        mocked_md5_instance.hexdigest.return_value = empty_email_hash

        gravatar_url = auth_util.get_user_gravatar_url(email_empty)
        expected_url_empty = f"https://www.gravatar.com/avatar/{empty_email_hash}?{expected_query_params}"
        assert gravatar_url == expected_url_empty

        # Reset mocks for the next test cases
        mock_md5.reset_mock()
        mock_urlencode.reset_mock()

        # case 3: get_user_gravatar_url with a different email
        email_diff = "anotheruser@domain.com"
        diff_email_hash = hashlib.md5(email_diff.lower().encode("utf-8")).hexdigest()
        mocked_md5_instance.hexdigest.return_value = diff_email_hash

        gravatar_url = auth_util.get_user_gravatar_url(email_diff)
        expected_url_diff = (
            f"https://www.gravatar.com/avatar/{diff_email_hash}?{expected_query_params}"
        )
        assert gravatar_url == expected_url_diff
