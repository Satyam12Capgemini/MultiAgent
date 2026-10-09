from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserOut
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.errors import UnauthorizedError
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        extra={"email": user.email, "customer_id": user.customer_id}
    )
    refresh_token = create_refresh_token(subject=user.id, role=user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user=UserOut.model_validate(user)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        user_id = payload.get("sub")
    except Exception:
        raise UnauthorizedError("Invalid refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        extra={"email": user.email, "customer_id": user.customer_id}
    )
    new_refresh = create_refresh_token(subject=user.id, role=user.role)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=3600,
        user=UserOut.model_validate(user)
    )

@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
