import string
import random
import hashlib
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from urllib.parse import urlencode
from .logging import AppLogger
from ..config import get_settings, Environment

logger = AppLogger().get_logger()


class AuthUtil:
    """
    Utilities for authentication
    """

    def __init__(self):
        self.settings = get_settings()
        pass

    def __generate_random_string__(self, length: int) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def generate_referral_code(self) -> str:
        return self.__generate_random_string__(5)

    def generate_api_key(self) -> str:
        return self.__generate_random_string__(30)

    def generate_login_token(self) -> str:
        return self.__generate_random_string__(20)

    def create_jwt_token(self, email: str) -> str:
        """
        Create a JWT token for the given email.

        Parameters:

            email (str): The email address of the user.

        Returns:

            str: A JWT token string.
        """
        to_encode = {
            "sub": email,
            "exp": datetime.now()
            + timedelta(minutes=self.settings.JWT_EXPIRATION_MINUTES),
        }
        return jwt.encode(
            to_encode,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )

    def verify_jwt_token(self, token: str) -> Optional[str]:
        """
        Verify a JWT token and extract the email.

        Parameters:

            token (str): The JWT token to verify.

        Returns:

            [str]: The email extracted from the token if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM],
            )
            return payload.get("sub")
        except JWTError:
            return None

    def send_magic_link(
        self, url: str, email: str, token: str, base_url: Optional[str] = None
    ) -> bool:
        """
        Send a magic link to the provided email address.

        Parameters:

            url (str): The URL for the magic link.

            email (str): The email address to send the magic link to.

            token (str): The JWT token to include in the magic link.

            base_url (str): Base url of the magic link. In PRODUCTION, it will use env URL_PREFIX.

        Returns:

            bool: True if the magic link was sent successfully, False otherwise.

        """
        if self.settings.ENVIRONMENT == Environment.PRODUCTION.value:
            base_url = self.settings.URL_PREFIX

        link = f"{base_url}{url}?token={token}"
        message = Mail(
            from_email=self.settings.SENDGRID_FROM_EMAIL,
            to_emails=email,
            subject="Your Magic Link Login",
            html_content=f"Click <a href='{link}'>here</a> to log in.",
        )
        try:
            sg = SendGridAPIClient(self.settings.SENDGRID_API_KEY)
            response = sg.send(message)
            if response.status_code == 202:
                return True
            else:
                logger.info(response.status_code)
                logger.info(response.body)
                return False
        except Exception as e:
            logger.error(f"Exception in send_magic_link in AuthUtil: {e}")
            return False

    def get_user_gravatar_url(
        self,
        email: str,
        default_url: str = "identicon",
        size: int = 40,
    ) -> str:
        """
        Get a user's gravatar url with email address

        Parameters:

            email (str): The email address to get the user's gravatar url

            default_url (str): Default image URL to use if no gravatar is found

            size (int): Gravatar size in pixels

        Returns:

            str: The user's gravatar URL

        """
        # Encode the email to lowercase and then to bytes
        email_encoded = email.lower().encode("utf-8")

        # Generate the MD5 hash of the email
        email_hash = hashlib.md5(email_encoded).hexdigest()

        # Construct the URL with encoded query parameters
        query_params = urlencode({"d": default_url, "s": str(size)})
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?{query_params}"

        return gravatar_url
