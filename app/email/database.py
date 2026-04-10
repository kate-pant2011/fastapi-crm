from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.database.common import order, get_all_and_total
from app.models.email import Email

async def get_all_emails(session, limit, offset, is_admin, user_id, scope):
    stmt = select(Email)

    if (not is_admin) or (is_admin and scope == "available"):
        stmt = stmt.where(
            or_(
                Email.owner_id == None,
                Email.owner_id == user_id
            )
        )

    if scope == "mine":
        stmt = stmt.where(Email.owner_id == user_id)

    result = await get_all_and_total(session, stmt, limit, offset)
    return result

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


async def add_email(session, items, server, port, password, user_id):
    email =Email(
        server = server,
        port = port, 
        login = items.login,
        password = password,
        creator_id = user_id,
        owner_id = items.assigned_user_id
    )

    session.add(email)
    await session.flush()
    return email

