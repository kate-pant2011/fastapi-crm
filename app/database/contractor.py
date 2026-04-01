from sqlalchemy import select
from app.models.contractor import Contractor
from sqlalchemy.orm import selectinload
from .common import order, get_all_and_total


async def get_all_contractors(session, limit, offset):
    stmt = select(Contractor).where(Contractor.is_archived == False)

    stmt = order(stmt=stmt, model=Contractor)

    result = await get_all_and_total(session, stmt, limit, offset)
    return result


async def get_contractor_by_name(session, name):
    result = await session.execute(
        select(Contractor)
        .where(Contractor.name == name)
    )
    return result.scalar_one_or_none()


async def get_contractor_by_id(session, id):

    result = await session.execute(
        select(Contractor)
        .where(Contractor.id == id)
    )
    return result.scalar_one_or_none()


async def add_contractor(session, data):
    contractor = Contractor(
        name=data.name,
        email=data.email,
        description=data.description,
    )

    session.add(contractor)
    await session.flush()
    return contractor
