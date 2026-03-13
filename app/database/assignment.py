from sqlalchemy import select, update
from app.models.assignment import Assignment
from app.models.stage import Stage
from app.models.project import Project
from app.models.client import Client
from sqlalchemy.orm import selectinload


async def get_assignment_by_id(session, id, manager_id=None):
    stmt = (
        select(Assignment)
        .options(selectinload(Assignment.stage))
        .options(selectinload(Assignment.contractor))
        .options(selectinload(Assignment.user))
        .join(Assignment.stage)
        .join(Stage.project)
        .join(Project.client)
        .where(Assignment.id == id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_assignment(session, data):
    assignment = Assignment(
        name=data.name,
        description=data.description,
        stage_id=data.stage_id,
        user_id=data.user_id,
        contractor_id=data.contractor_id
    )

    session.add(assignment)
    await session.flush()
    return assignment
