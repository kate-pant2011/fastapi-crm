from sqlalchemy import select, update
from fastapi import HTTPException
from app.models.company import Company
from app.models.client import Client
from sqlalchemy.orm import selectinload


async def get_filtered_companies(session, manager_id, client_id):
    stmt = select(Company).join(Company.client).where(Company.is_archived == False)

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_company_by_id(session, manager_id, company_id):
    stmt = (
        select(Company)
        .join(Company.client)
        .options(selectinload(Company.contracts))
        .where(Company.id == company_id)
        .where(Company.is_archived == False)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_company_by_inn(session, inn: str):
    result = await session.execute(select(Company).where(Company.inn == inn))

    return result.scalar_one_or_none()


async def add_company(session, data):
    company = Company(
        name=data.name,
        inn=data.inn,
        client_id=data.client_id,
    )

    session.add(company)
    await session.flush()
    return company
