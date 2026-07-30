from sqlalchemy import select, or_
from app.models.doc_template import DocumentTemplate
from sqlalchemy.orm import selectinload
from .common import order, get_all_and_total


async def get_all_doc_templates(session, scope, limit, offset, is_admin, user_id):
    stmt = (
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.creator))
        .join(DocumentTemplate.creator)
    )

    if scope == "mine":
        stmt = stmt.where(DocumentTemplate.creator_id == user_id)

    if scope == "available" or not is_admin:
        stmt = stmt.where(
            or_(
                DocumentTemplate.creator_id == user_id,
                DocumentTemplate.is_public == True
            )
        )

    stmt = order(stmt=stmt, model=DocumentTemplate)

    result = await get_all_and_total(session, stmt, limit, offset)
    return result


async def get_doc_template_by_name(session, name: str):
    stmt = (
        select(DocumentTemplate)
        .where(DocumentTemplate.name == name)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_doc_template_by_id(session, id: int):
    stmt = (
        select(DocumentTemplate)
        .options(selectinload(DocumentTemplate.creator))
        .where(DocumentTemplate.id == id)
        .options(selectinload(DocumentTemplate.file))
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_doc_template(session, data, creator_id):
    template = DocumentTemplate(
        name=data.name, 
        description=data.description,
        is_public=data.is_public,
        creator_id=creator_id
    )

    session.add(template)
    await session.flush()
    return template