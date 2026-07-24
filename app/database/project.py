from sqlalchemy import select, or_
from app.models.project import Project
from app.models.client import Client
from app.models.stage import Stage
from app.models.contract import Contract
from app.models.assignment import Assignment
from sqlalchemy.orm import selectinload
from sqlalchemy import exists, and_
from .common import apply_sorting, order, get_all_and_total


async def get_filtered_projects(session, manager_id, query, sorting_rules):
    stmt = select(Project).join(Project.client)
    if query.is_archived is None:
        stmt = stmt.where(Project.is_archived.is_(False))
    if query.is_archived is True:
        stmt = stmt.where(Project.is_archived.is_(True))

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if query.client_id is not None:
        stmt = stmt.where(Client.id == query.client_id)

    if query.contract_id is not None:
        stmt = stmt.join(Project.contract).where(Contract.id == query.contract_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Project, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = order(stmt=stmt, model=Project)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_project_by_id(session, id, manager_id=None, executor_id=None):
    stmt = (
        select(Project)
        .options(selectinload(Project.contract).selectinload(Contract.company))
        .options(selectinload(Project.client).selectinload(Client.manager))
        .options(selectinload(Project.stages))
        .options(selectinload(Project.files))
        .join(Project.client)
        .where(Project.id == id)
    )

    conditions = []

    if manager_id is not None:
        conditions.append((Client.manager_id == manager_id))

    if executor_id is not None:
        conditions.append(Project.stages.any(
            Stage.assignments.any(Assignment.user_id == executor_id)
            )
        )

    if conditions:
        stmt = stmt.where(or_(*conditions))

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_by_for_ctx(session, id):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.contract).selectinload(Contract.company),
            selectinload(Project.contract).selectinload(Contract.branch),
            selectinload(Project.client).selectinload(Client.manager),
            selectinload(Project.stages),
            selectinload(Project.files),
        )
        .join(Project.client)
        .where(Project.id == id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_by_name(session, name):
    result = await session.execute(select(Project).where(Project.name == name))
    return result.scalars().unique().one_or_none()


async def add_project(session, data):
    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        client_id=data.client_id,
        contract_id=data.contract_id,
    )

    session.add(project)
    await session.flush()
    return project
