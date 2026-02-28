from app.models_loader import RefreshToken
from sqlalchemy import select, update


class TokenReuseDetection(Exception):
    def __init__(self, user_id):
        self.user_id = user_id


async def add_refresh_jwt(session, user_id, exp, jti, device):
    refresh = RefreshToken(
        jti=jti, device=device, is_active=True, exp=exp, user_id=user_id
    )

    session.add(refresh)
    await session.flush()
    return refresh


async def verify_refresh_jwt(session, jti):
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.jti == jti).with_for_update()
    )

    refresh = result.scalar_one_or_none()

    if not refresh:
        return None

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


async def deactivate_user_refresh(session, user_id, jti):
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .where(RefreshToken.jti == jti)
        .values(is_active=False)
    )


async def get_refresh_by_jwt(session, jti):
    result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))

    refresh = result.scalar_one_or_none()
    if not refresh:
        return None

    return refresh
