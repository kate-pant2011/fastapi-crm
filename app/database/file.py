from app.models.file import File
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_all_files(session, query, entity_id, entity_type, sorting_rules):
    stmt = select(File)

    if entity_type == "project":
        stmt = stmt.where(File.project_id == entity_id)

    elif entity_type == "client":
        stmt = stmt.where(File.client_id == entity_id)

    if not query.sort:
        stmt = order(stmt=stmt, model=File)

    else:
        stmt = apply_sorting(stmt=stmt, model=File, sort=query.sort, sorting_rules=sorting_rules)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def add_file(session, data, user_id):
    file = File(
        name=data.filenames.original,
        unique_name=data.filenames.unique,
        path=data.path,
        size=data.size,
        mime_type=data.mime_type,
        creator_id=user_id,
    )

    session.add(file)
    await session.flush()
    return file


async def get_file_by_id(session, file_id):
    stmt = (
        select(File)
        .options(selectinload(File.creator))
        .options(selectinload(File.project))
        .options(selectinload(File.client))
        .where(File.id == file_id)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


