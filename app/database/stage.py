from sqlalchemy import select, or_
from app.models.stage import Stage
from app.models.project import Project
from app.models.client import Client
from app.models.user import User
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_filtered_stages(session, manager_id, project_id, query):
    stmt = (
        select(Stage)
        .join(Stage.project)
        .join(Project.client)
        .where(Stage.is_archived == False)
        .where(Project.id == project_id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Stage, sort=query.sort)
    else:
        stmt = stmt.order_by(Stage.position)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_stage_by_id(session, id, user_id, is_admin):
    stmt = (
        select(Stage)
        .options(
            selectinload(Stage.project)
            .selectinload(Project.client)
            .selectinload(Client.manager)
        )
        .options(selectinload(Stage.assignments))
        .join(Stage.project)
        .join(Project.client)
        .where(Stage.id == id)
    )

    if not is_admin:
        stmt = stmt.where(
            or_(Client.manager_id == user_id, Stage.assignments.any(User.id == user_id))
        )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_stage(session, data, position):
    stage = Stage(
        name=data.name,
        position=position,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        project_id=data.project_id,
    )

    session.add(stage)
    await session.flush()
    return stage
