from app.models_loader import PasswordResetToken
from sqlalchemy import select, update
from datetime import datetime, timezone

class ResetTokenReuseDetection(Exception):
    def __init__(self, user_id):
        self.user_id = user_id


async def add_reset_jwt(session, user_id, exp, jti, device):
    reset = PasswordResetToken(
        jti=jti, device=device, exp=exp, user_id=user_id
    )

    session.add(reset)
    await session.flush()
    return reset


async def verify_reset_jwt(session, jti):
    result = await session.execute(
        select(PasswordResetToken).where(PasswordResetToken.jti == jti).with_for_update()
    )

    reset = result.scalar_one_or_none()

    if not reset:
        return None

    if reset.used_at is not None:
        raise ResetTokenReuseDetection(reset.user_id)

    return reset


async def deactivate_all_user_reset_jwt(session, user_id):
    await session.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user_id)
        .where(PasswordResetToken.used_at.is_(None))
        .values(used_at=datetime.now(timezone.utc))
    )