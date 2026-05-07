from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user_schema import CurrentUserResponse


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    confirmPassword: str = Field(min_length=6, max_length=72)
    phone: Optional[str] = None

    @field_validator('confirmPassword')
    @classmethod
    def passwords_match(cls, value: str, info):
        if 'password' in info.data and value != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return value


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    resetToken: Optional[str] = None
    resetUrl: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=6, max_length=72)
    confirmPassword: str = Field(min_length=6, max_length=72)

    @field_validator('confirmPassword')
    @classmethod
    def reset_passwords_match(cls, value: str, info):
        if 'password' in info.data and value != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return value


class ResetPasswordResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    deviceName: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class LogoutResponse(BaseModel):
    message: str


class SessionResponse(BaseModel):
    id: int
    deviceName: Optional[str] = None
    userAgent: Optional[str] = None
    ipAddress: Optional[str] = None
    isActive: bool
    expiresAt: str
    lastUsedAt: Optional[str] = None
    createdAt: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = 'bearer'
    user: CurrentUserResponse
