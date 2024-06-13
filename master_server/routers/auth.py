from datetime import datetime
from fastapi import APIRouter, Query, Depends, Request
from ..database.config import get_session, AsyncSession
from ..database.user.service import UserService
from ..database.user.model import User
from ..utils.logging import AppLogger
from ..utils.auth import AuthUtil
from ..schemas.auth import SendMagicLinkRequest, VerifyMagicLinkResponse
from ..dependencies.common import get_client_ip
from ..config import get_settings
from ..exceptions.http import NotFoundHTTPException, AuthFailedHTTPException

logger = AppLogger().get_logger()

router = APIRouter(
    prefix="/auth", tags=["auth"], responses={404: {"error": "Not found"}}
)


@router.post("/send-magic-link", response_model=bool)
async def send_magic_link(
    request: Request,
    model: SendMagicLinkRequest,
    client_ip: str = Depends(get_client_ip),
    db_session: AsyncSession = Depends(get_session),
):
    """
    Send magic link and add user to the table.

    Parameters:

        email (str): email address that will receive magic link

    Returns:

        bool: True if the magic link is sent to the email address

    Raises:

        AuthFailedHTTPException: If user is already banned. In this case, verification email won't be sent.
    """
    settings = get_settings()
    user_service = UserService(db_session=db_session)
    auth_util = AuthUtil()
    login_token = auth_util.generate_login_token()

    user = await user_service.find_by_email(email=model.email)

    if user is None:
        user = await user_service.add_user(
            User(
                email=model.email,
                token=login_token,
                created_with_ip=client_ip,
                last_login_with_ip=client_ip,
                last_login_on=datetime.now(),
            )
        )
    else:
        if user.banned:
            raise AuthFailedHTTPException(msg="Banned user")

        user = await user_service.update_user(
            user=user,
            token=login_token,
            last_login_with_ip=client_ip,
            last_login_on=datetime.now(),
        )

    return AuthUtil().send_magic_link(
        base_url=request.base_url,
        url="auth/verify-magic-link",
        email=model.email,
        token=login_token,
    )


@router.get("/verify-magic-link", response_model=VerifyMagicLinkResponse)
async def verify_magic_link(
    token: str = Query(..., description="Magic link verification token"),
    db_session: AsyncSession = Depends(get_session),
):
    """
    Verify magic link

    Parameters:

        token (str): The magic link token to verify.

    Returns:

        token (str): jwt authoirization token

        user_id (int): user id in database

    Raises:

        NotFoundHTTPException: token is not found.
    """

    user_service = UserService(db_session=db_session)
    user = await user_service.find_by_token(token=token)
    if not user:
        raise NotFoundHTTPException(msg="token not found")

    user = await user_service.update_user(user, is_verified=True)

    jwt_token = AuthUtil().create_jwt_token(email=user.email)
    return VerifyMagicLinkResponse(token=jwt_token, user_id=user.id)
