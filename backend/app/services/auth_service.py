from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, req: UserRegisterRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == req.email.lower()))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        hashed_password = get_password_hash(req.password)
        new_user = User(
            name=req.name,
            email=req.email.lower(),
            password_hash=hashed_password,
            role=req.role
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        token = create_access_token(subject=new_user.id, role=new_user.role.value)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=new_user.id,
                name=new_user.name,
                email=new_user.email,
                role=new_user.role,
                created_at=new_user.created_at.isoformat()
            )
        )

    @staticmethod
    async def login_user(db: AsyncSession, req: UserLoginRequest) -> TokenResponse:
        result = await db.execute(select(User).where(User.email == req.email.lower()))
        user = result.scalar_one_or_none()
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        token = create_access_token(subject=user.id, role=user.role.value)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at.isoformat()
            )
        )
