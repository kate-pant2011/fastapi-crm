from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.email import Email

async def get_email_by_id(session, id):
    result = await session.execute(
        select(Email)
        .where(Email.id == id)
    )
    email = result.scalar_one_or_none()
    return email


async def get_email_by_login(session, login):
    result = await session.execute(
        select(Email).where(Email.login == login)
    )

    email = result.scalar_one_or_none()
    return email


async def add_email(session, items, password, user_id):
    email =Email(
        server = items.server,
        port = items.port, 
        login = items.login,
        password = password,
        personal = items.personal,
        creator_id = user_id

    )

    session.add(email)
    await session.flush()
    return email

