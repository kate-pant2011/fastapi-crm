from sqlalchemy import select, update
from app.models.contractor import Contractor
from sqlalchemy.orm import selectinload


async def get_all_contractors(session):
    result = await session.execute(
        select(Contractor).where(Contractor.is_archived == False)
    )
    return result.scalars().all()


async def get_contractor_by_name(session, name):
    result = await session.execute(
        select(Contractor)
        .options(selectinload(Contractor.contracts))
        .where(Contractor.name == name)
    )
    return result.scalar_one_or_none()


async def get_contractor_by_id(session, id):

    result = await session.execute(
        select(Contractor)
        .options(selectinload(Contractor.contracts))
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
