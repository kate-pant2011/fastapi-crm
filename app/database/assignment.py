from sqlalchemy import select, or_
from app.models.assignment import Assignment
from app.models.stage import Stage
from app.models.project import Project
from app.models.client import Client
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_filtered_assignments(session, query, sorting_rules, user_id=None):
    stmt = select(Assignment)

    if user_id is not None:
        stmt = stmt.where(Assignment.user_id == user_id)

    if query.scope is not None:
        if query.scope == "users":
            stmt = stmt.where(Assignment.user_id.is_not(None))

        elif query.scope == "contractors":
            stmt = stmt.where(Assignment.contractor_id.is_not(None))

    if query.is_done is True:
        stmt = stmt.where(Assignment.is_done.is_(True))
    else:
        stmt = stmt.where(Assignment.is_done.is_(False))

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Assignment, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = order(stmt=stmt, model=Assignment)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_assignment_by_id(
        session, id, manager_id=None, executor_id=None
):
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

    conditions = []

    if manager_id is not None:
        conditions.append((Client.manager_id == manager_id))
    
    if executor_id is not None:
        conditions.append((Assignment.user_id == executor_id))

    if conditions:
        stmt = stmt.where(or_(*conditions))

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_assignment(session, data):
    assignment = Assignment(
        name=data.name,
        description=data.description,
        stage_id=data.stage_id,
        user_id=data.user_id,
        contractor_id=data.contractor_id,
    )

    session.add(assignment)
    await session.flush()
    return assignment
