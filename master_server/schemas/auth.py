from pydantic import BaseModel, EmailStr


class SendMagicLinkRequest(BaseModel):
    email: EmailStr


class VerifyMagicLinkResponse(BaseModel):
    token: str
    user_id: int
