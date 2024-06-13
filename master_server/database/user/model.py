import string
from typing import Optional
from datetime import datetime
from pydantic import field_validator
from sqlmodel import Field, Column, JSON
from ..base.model import Base, TimeStampMixin
from master_server.enums.user_enums import UserRoleEnum
from master_server.utils.auth import AuthUtil


class User(Base, TimeStampMixin, table=True):
    """
    Represents a user in the database.

    Attributes:

        username (str): The unique username of the user.

        first_name (str): The first name of the user.

        last_name (str): The last name of the user.

        date_of_birth (Optional[datetime]): The date of birth of the user.

        address (Optional[dict]): The address of the user (stored as JSONB).

        phone (Optional[dict]): The phone information of the user (stored as JSONB).

        email (str): The unique email address of the user.

        created_with_ip (str): The IP address from which the user was created.

        last_login_on (datetime): The last login timestamp of the user.

        last_login_with_ip (str): The IP address from which the user last logged in.

        banned (bool): Indicates if the user is banned.

        role (UserRoleEnum): The role of the user (either USER or RESELLER).

        referral_code (str): The referral code of the user.

        token (str): Random token for magic link verification that will be generated every log in.

        api_key (str): api_key for the user.

        balance (int): User's wallet balance.

        is_verified (bool): Indicate whether user is verified magic link.

    """

    token: str = Field(nullable=False, default_factory=AuthUtil().generate_login_token)
    referral_code: str = Field(
        nullable=False, default_factory=AuthUtil().generate_referral_code
    )
    email: str = Field(index=True, unique=True, nullable=False)
    is_verified: bool = Field(default=False)
    banned: bool = Field(default=False)
    balance: int = Field(default=0)
    role: UserRoleEnum = Field(default=UserRoleEnum.USER, nullable=False)
    created_with_ip: str = Field(nullable=False, default="localhost")
    last_login_on: datetime = Field(default_factory=datetime.now, nullable=False)
    last_login_with_ip: str = Field(default="localhost", nullable=False)

    username: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    date_of_birth: Optional[datetime] = Field(default=None)
    address: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    phone: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    api_key: Optional[str] = Field(default_factory=AuthUtil().generate_api_key)
    # used_referral_code: Optional[str] = Field(default=None)

    @field_validator("referral_code")
    def validate_referral_code(cls, value):
        if value and (
            len(value) != 5
            or not all(c in string.ascii_letters + string.digits for c in value)
        ):
            raise ValueError(
                "referral_code must be 5 characters long and consist of alphanumeric characters"
            )
        return value

    @field_validator("token")
    def validate_token(cls, value):
        if value and (
            len(value) != 20
            or not all(c in string.ascii_letters + string.digits for c in value)
        ):
            raise ValueError(
                "token must be 20 characters long and consist of alphanumeric characters"
            )
        return value

    @field_validator("email")
    def validate_email(cls, value):
        if len(value) > 256:
            raise ValueError("Email address must not exceed 256 characters")
        if "@" not in value or "." not in value:
            raise ValueError("Email address must be valid")
        return value

    @field_validator("username")
    def validate_username(cls, value):
        if value and len(value) > 30:
            raise ValueError("Username must not exceed 30 characters")
        if value and not all(
            c in string.ascii_letters + string.digits + "_" for c in value
        ):
            raise ValueError(
                "Username can only contain alphanumeric characters and underscores"
            )
        return value

    @field_validator("first_name")
    def validate_first_name(cls, value):
        if value and len(value) > 50:
            raise ValueError("First name must not exceed 50 characters")
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value):
        if value and len(value) > 50:
            raise ValueError("Last name must not exceed 50 characters")
        return value

    @field_validator("created_with_ip", "last_login_with_ip")
    def validate_ip(cls, value):
        if value and len(value) > 45:  # IPv4 and IPv6 length consideration
            raise ValueError("IP address must not exceed 45 characters")
        return value

    @field_validator("balance")
    def validate_balance(cls, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        return value

    @field_validator("api_key")
    def validate_api_key(cls, value):
        if value and len(value) != 30:
            raise ValueError("api_key must be 30 characters long")
        return value
