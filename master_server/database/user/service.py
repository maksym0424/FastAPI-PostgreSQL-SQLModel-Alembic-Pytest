import random
import string
from typing import Optional
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from .model import User
from .exception import UsernameAlreadyTaken, EmailAlreadyTaken
from master_server.utils.auth import AuthUtil
from ..base.service import BaseService


class UserService(BaseService):
    """
    User Service
    """

    async def add_user(self, user: User) -> User:
        """
        Add a user to the table.

        Parameters:

            user (User): User model to add.

        Returns:

            Optional[User]: Updated user model after save.

        Raises:

            UsernameAlreadyTaken: When user.username is already taken.

            EmailAlreadyTaken: When user.email is already taken.

        """
        is_username_exist = await self.is_username_exist(username=user.username)

        if is_username_exist == True:
            raise UsernameAlreadyTaken(user.username)

        is_email_exist = await self.is_email_exist(email=user.email)
        if is_email_exist == True:
            raise EmailAlreadyTaken(user.email)

        await user.save(self.db_session)

        return user

    async def update_user(self, user: User, **kwargs) -> User:
        """
        Update user.

        Parameters:

            user (User): User model to update.

        Returns:

            Optional[User]: Updated user model after save.

        Raises:

            UsernameAlreadyTaken: When user.username is already taken.

            EmailAlreadyTaken: When user.email is already taken.

        """
        if "username" in kwargs:
            is_username_exist = await self.is_username_exist(
                username=kwargs["username"]
            )
            if is_username_exist == True:
                raise UsernameAlreadyTaken(kwargs["username"])

        if "email" in kwargs:
            is_email_exist = await self.is_email_exist(email=kwargs["email"])
            if is_email_exist == True:
                raise EmailAlreadyTaken(kwargs["email"])

        await user.update(self.db_session, **kwargs)
        return user

    async def find_by_api_key(self, api_key: str) -> Optional[User]:
        """
        Retrieve a user by their api_key.

        Parameters:

            api_key (str): The api_key of the user to retrieve.

        Returns:

            Optional[User]: The User object if found, otherwise None.

        """
        statement = select(User).where(User.api_key == api_key)

        try:
            result = await self.db_session.exec(statement)
            return result.one()
        except NoResultFound:
            return None

    async def find_by_token(self, token: str) -> Optional[User]:
        """
        Retrieve a user by their token.

        Parameters:

            token (str): The token of the user to retrieve.

        Returns:

            Optional[User]: The User object if found, otherwise None.

        """
        statement = select(User).where(User.token == token)

        try:
            result = await self.db_session.exec(statement)
            return result.one()
        except NoResultFound:
            return None

    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Parameters:

            email (str): The email address of the user to retrieve.

        Returns:

            Optional[User]: The User object if found, otherwise None.

        """
        statement = select(User).where(User.username == username)

        try:
            result = await self.db_session.exec(statement)
            return result.one()
        except NoResultFound:
            return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Parameters:

            email (str): The email address of the user to retrieve.

        Returns:

            Optional[User]: The User object if found, otherwise None.

        """
        statement = select(User).where(User.email == email)

        try:
            result = await self.db_session.exec(statement)
            return result.one()
        except NoResultFound:
            return None

    async def is_username_exist(self, username: Optional[str]) -> bool:
        """
        Return if username is already taken.

        Parameters:

            username (Optional[str]): User name to check

        Returns:

            bool: If it is already taken, return True, otherwise return False.
        """
        if not username:
            return False

        user = await self.find_by_username(username)
        if not user:
            return False
        return True

    async def is_email_exist(self, email: Optional[str]) -> bool:
        """
        Return if email is already taken.

        Parameters:

            email (Optional[str]): Email to check

        Returns:

            bool: If it is already taken, return True, otherwise return False.
        """
        if not email:
            return False

        user = await self.find_by_email(email)
        if not user:
            return False
        return True
