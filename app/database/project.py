from sqlalchemy import select, update
from app.models.project import Project
from app.models.client import Client
from sqlalchemy.orm import selectinload


async def get_filtered_projects(session, manager_id, client_id):
    stmt = (
        select(Project)
        .join(Project.client)
        .where(Project.is_archived == False)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)
    
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_project_by_id(session, id, manager_id):
    stmt = (
        select(Project)
        .options(selectinload(Project.contract))
        .options(selectinload(Project.client))
        .options(selectinload(Project.stages))
        .join(Project.client)
        .where(Project.id == id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_by_name(session, name):
    result = await session.execute(
        select(Project)
        .where(Project.name == name)
    )
    return result.scalar_one_or_none()


async def add_project(session, data):
    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        client_id=data.client_id,
        contract_id=data.contract_id
    )

    session.add(project)
    await session.flush()
    return project