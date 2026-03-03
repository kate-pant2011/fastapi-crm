from sqlalchemy import select, update, or_
from app.models.stage import Stage, StageTemplate
from app.models.project import Project
from app.models.client import Client
from app.models.user import User
from sqlalchemy.orm import selectinload


async def get_filtered_stages(session, manager_id, project_id):
    stmt = (
        select(Stage)
        .join(Stage.project)
        .join(Project.client)
        .where(Stage.is_archived == False)
        .where(Project.id == project_id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalars().all()


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


async def add_stage(session, data):
    stage = Stage(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        project_id=data.project_id,
    )

    session.add(stage)
    await session.flush()
    return stage


async def add_stage_template(session, data, creator_id):
    template = StageTemplate(
        name=data.name, stage_list=data.stage_list, user_id=creator_id
    )

    session.add(template)
    await session.flush()
    return template
