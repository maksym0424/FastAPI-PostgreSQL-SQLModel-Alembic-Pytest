from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class AddressSchema(BaseModel):
    address: str
    city: str
    country: str
    state: str
    zip_code: str


class PhoneSchema(BaseModel):
    country_code: str
    number: str


class UserResponseSchema(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    profile_url: Optional[str]
    date_of_birth: Optional[datetime]
    address: Optional[AddressSchema]
    phone: Optional[PhoneSchema]
    email: Optional[str]
    referral_code: Optional[str]
    api_key: Optional[str]


class UserPatchSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = datetime.now()
    address: Optional[AddressSchema] = None
    phone: Optional[PhoneSchema] = None
    email: Optional[EmailStr] = None
    api_key: Optional[str] = None

    @field_validator("date_of_birth", mode="before")
    def parse_date_of_birth(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}")
        return value

    @field_validator("address", mode="before")
    def parse_address(cls, value):
        if isinstance(value, dict):
            return AddressSchema(**value)
        return value

    @field_validator("phone", mode="before")
    def parse_phone(cls, value):
        if isinstance(value, dict):
            if len(value["number"]) < 10:
                raise ValueError("Phone number is too short")

            if len(value["number"]) > 15:
                raise ValueError("Phone number is too long")

            return PhoneSchema(**value)
        return value
