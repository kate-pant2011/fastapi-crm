from sqlalchemy import select
from app.models.company import Company
from app.models.client import Client
from sqlalchemy.orm import selectinload
from .common import apply_sorting, order, get_all_and_total


async def get_filtered_companies(session, manager_id, query, sorting_rules):
    stmt = select(Company).join(Company.client).where(Company.is_archived == False)

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if query.client_id is not None:
        stmt = stmt.where(Client.id == query.client_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Company, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = order(stmt=stmt, model=Company)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_company_by_id(session, company_id, manager_id=None):
    stmt = (
        select(Company)
        .join(Company.client)
        .options(selectinload(Company.contracts))
        .options(selectinload(Company.client))
        .where(Company.id == company_id)
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
