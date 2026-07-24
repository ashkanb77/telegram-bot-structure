from pydantic import BaseModel


class RegisterSchema(BaseModel):
    phone_number: str


class LoginSchema(BaseModel):
    otp: str
    phone_number: str


class BackendAccessTokenRequestSchema(BaseModel):
    access_token: str


class BackendRefreshTokenRequestSchema(BaseModel):
    refresh_token: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
