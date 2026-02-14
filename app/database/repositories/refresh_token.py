from app.models_loader import RefreshToken
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

class TokenReuseDetection(Exception):
    def __init__(self, user_id):
        self.user_id = user_id

class RefreshTokenNotFound(Exception):
    pass

async def add_refresh_jwt(session, user_id, exp, jti, device):
    refresh = RefreshToken(
        jti=jti,
        device=device,
        is_active=True,
        exp=exp, 
        user_id=user_id
    )

    session.add(refresh)
    await session.flush()
    return refresh

async def verify_refresh_jwt(session, jti):
    result = await session.execute(
        select(RefreshToken)
        .where(RefreshToken.jti == jti)
        .with_for_update()
    )

    refresh = result.scalar_one_or_none()

    if not refresh:
        raise RefreshTokenNotFound()

    if not refresh.is_active:
        raise TokenReuseDetection(refresh.user_id)

    refresh.is_active = False

    return refresh

async def deactivate_all_user_refresh(session, user_id):
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .where(RefreshToken.is_active == True)
        .values(is_active=False)
    )