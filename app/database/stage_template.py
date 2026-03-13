from sqlalchemy import select
from app.models.user import User
from app.models.stage_template import StageTemplate
from sqlalchemy.orm import selectinload
from .common import order, get_all_and_total


async def get_all_stage_templates(session, creator_id, limit, offset):
    stmt = (
        select(StageTemplate)
        .join(StageTemplate.creator)
        .where(StageTemplate.is_archived == False)
    )

    if creator_id is not None:
        stmt = stmt.where(User.id == creator_id)

    stmt = order(stmt=stmt, model=StageTemplate)

    result = await get_all_and_total(session, stmt, limit, offset)
    return result


async def get_stage_template_by_name(session, name: str):
    stmt = select(StageTemplate).where(StageTemplate.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_stage_template_by_id(session, id: int):
    result = await session.execute(
        select(StageTemplate)
        .options(selectinload(StageTemplate.creator))
        .where(StageTemplate.id == id)
    )
    return result.scalar_one_or_none()


async def add_stage_template(session, data, creator_id):
    template = StageTemplate(
        name=data.name, stage_list=data.stage_list, creator_id=creator_id
    )

    session.add(template)
    await session.flush()
    return template
