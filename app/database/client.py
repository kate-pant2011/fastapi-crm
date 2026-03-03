from sqlalchemy import select, update
from app.models.client import Client
from app.models.company import Company
from sqlalchemy.orm import selectinload


async def get_filtered_clients(session, manager_id):
    stmt = select(Client).where(Client.is_archived == False)

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_client_by_id(session, id, manager_id):
    stmt = (
        select(Client)
        .options(selectinload(Client.companies))
        .options(selectinload(Client.projects))
        .where(Client.id == id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_client_by_name(session, name):
    result = await session.execute(
        select(Client)
        .options(selectinload(Client.companies))
        .where(Client.name == name)
    )
    return result.scalar_one_or_none()


async def add_client(session, data, manager_id):
    client = Client(
        name=data.name,
        email=data.email,
        telephone=data.telephone,
        manager_id=manager_id,
    )

    session.add(client)
    await session.flush()
    return client
