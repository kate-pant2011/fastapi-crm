from sqlalchemy import select
from app.models.client import Client
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_filtered_clients(session, manager_id, query):
    stmt = select(Client).join(Client.manager).where(Client.is_archived == False)

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Client, sort=query.sort)
    else:
        stmt = order(stmt=stmt, model=Client)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_client_by_id(session, id, manager_id):
    stmt = (
        select(Client)
        .options(selectinload(Client.companies))
        .options(selectinload(Client.projects))
        .options(selectinload(Client.manager))
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
