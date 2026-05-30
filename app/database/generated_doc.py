from app.models.generated_doc import GeneratedDocument
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .common import order, get_all_and_total

async def get_all_generated_docs(session, user_id, query):
    stmt = (
        select(GeneratedDocument)
        .options(selectinload(GeneratedDocument.file))
        .where(GeneratedDocument.creator_id == user_id)
    )

    stmt = order(stmt=stmt, model=GeneratedDocument)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def add_generated_doc(session, template_id, user_id, file_id):
    generated_doc = GeneratedDocument(
        template_id=template_id,
        file_id=file_id,
        creator_id=user_id,
    )

    session.add(generated_doc)
    await session.flush()
    return generated_doc


async def get_generated_doc_by_id(session, generated_doc_id):
    stmt = (
        select(GeneratedDocument)
        .options(selectinload(GeneratedDocument.creator))
        .options(selectinload(GeneratedDocument.template))
        .options(selectinload(GeneratedDocument.file))
        .where(GeneratedDocument.id == generated_doc_id)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()