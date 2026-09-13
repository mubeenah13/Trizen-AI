from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John Admin")
    email: EmailStr = Field(..., example="admin@trizen.ai")
    password: str = Field(..., min_length=6, max_length=100, example="securepassword123")
    role: UserRole = Field(default=UserRole.TEAM_MEMBER, example="ADMIN")

class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@trizen.ai")
    password: str = Field(..., example="securepassword123")

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    created_at: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
