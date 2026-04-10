from sqlalchemy import select, or_
from app.models.user import User
from app.models.email_template import EmailTemplate
from sqlalchemy.orm import selectinload
from .common import order, get_all_and_total


async def get_all_email_templates(session, scope, limit, offset, is_admin, user_id):
    stmt = (
        select(EmailTemplate)
        .join(EmailTemplate.creator)
    )
    if not is_admin:
        stmt = stmt.where(EmailTemplate.creator_id == user_id)

    elif scope == "mine":
        stmt = stmt.where(EmailTemplate.creator_id == user_id)

    elif scope == "available":
        stmt = stmt.where(
            or_(
                EmailTemplate.creator_id == user_id,
                EmailTemplate.is_public == True
            )
        )

    stmt = order(stmt=stmt, model=EmailTemplate)

    result = await get_all_and_total(session, stmt, limit, offset)
    return result


async def get_email_template_by_name(session, name: str):
    stmt = select(EmailTemplate).where(EmailTemplate.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_email_template_by_id(session, id: int):
    stmt = select(EmailTemplate).options(selectinload(EmailTemplate.creator)).where(EmailTemplate.id == id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_email_template(session, data, creator_id):
    template = EmailTemplate(
        name=data.name, 
        subject_content=data.subject_content,
        body_content=data.body_content,
        is_public=data.is_public,
        creator_id=creator_id
    )

    session.add(template)
    await session.flush()
    return template


