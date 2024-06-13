from fastapi import APIRouter, Depends
from ..database.config import get_session, AsyncSession
from ..database.user.model import User
from ..database.user.schema import UserResponseSchema, UserPatchSchema
from ..database.user.service import UserService
from ..database.user.exception import UsernameAlreadyTaken, EmailAlreadyTaken
from ..dependencies.auth import get_current_user, get_current_active_user
from ..exceptions.http import BadRequestHTTPException
from ..utils.logging import AppLogger
from ..utils.auth import AuthUtil


logger = AppLogger().get_logger()

router = APIRouter(
    prefix="/user", tags=["user"], responses={404: {"error": "Not found"}}
)


@router.get("", response_model=UserResponseSchema)
async def get_user(user: User = Depends(get_current_user)):
    """
    return logged in user information
    """

    return UserResponseSchema(
        **user.model_dump(), profile_url=AuthUtil().get_user_gravatar_url(user.email)
    )


@router.patch("", response_model=UserResponseSchema)
async def patch_user(
    model: UserPatchSchema,
    user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_session),
):
    """
    Patch user
    """
    user_service = UserService(db_session=db_session)

    try:
        new_user = await user_service.update_user(
            user=user, **(model.model_dump(exclude_none=True))
        )
        return UserResponseSchema(
            **new_user.model_dump(),
            profile_url=AuthUtil().get_user_gravatar_url(new_user.email),
        )
    except UsernameAlreadyTaken as e:
        logger.error(f"error in /user [PATCH]: {e.message}")
        raise BadRequestHTTPException(msg="Username is already taken")
    except EmailAlreadyTaken as e:
        logger.error(f"error in /user [PATCH]: {e.message}")
        raise BadRequestHTTPException(msg="Email is already taken")
