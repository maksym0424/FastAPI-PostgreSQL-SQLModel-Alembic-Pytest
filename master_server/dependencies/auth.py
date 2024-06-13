from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..database.config import get_session, AsyncSession
from ..database.user.model import User
from ..database.user.service import UserService
from ..utils.auth import AuthUtil
from ..exceptions.http import AuthFailedHTTPException, NotFoundHTTPException


class CustomBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.scheme.lower() == "bearer":
            return credentials.credentials
        raise AuthFailedHTTPException


oauth2_scheme = CustomBearer()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db_session: AsyncSession = Depends(get_session)
) -> User:
    """
    Authenticate user from bearer token and return user if it is authorized and not banned.
    """
    email = AuthUtil().verify_jwt_token(token)
    if email is None:
        raise AuthFailedHTTPException

    user = await UserService(db_session=db_session).find_by_email(email=email)

    if not user:
        raise NotFoundHTTPException("User not found")

    if user.banned:
        raise AuthFailedHTTPException(msg="Banned user")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if all required user details are provided
    """
    for field, value in current_user.model_dump().items():
        if value is None:
            raise AuthFailedHTTPException(msg=f"{field} not provided")

    return current_user
