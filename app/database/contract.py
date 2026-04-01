from sqlalchemy import select
from app.models.contract import Contract
from app.models.client import Client
from app.models.company import Company
from app.models.branch import Branch
from sqlalchemy.orm import selectinload
from .common import apply_sorting, get_all_and_total


async def get_filtered_contracts(session, manager_id, query, sorting_rules):
    stmt = (
        select(Contract)
        .join(Contract.company)
        .join(Company.client)
        .join(Contract.branch)
        .where(Contract.is_archived == False)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    if query.branch_id is not None:
        stmt = stmt.where(Branch.id == query.branch_id)

    if query.company_id is not None:
        stmt = stmt.where(Company.id == query.company_id)

    if query.sort:
        stmt = apply_sorting(stmt=stmt, model=Contract, sort=query.sort, sorting_rules=sorting_rules)
    else:
        stmt = stmt.order_by(Contract.created_at)

    result = await get_all_and_total(session, stmt, query.limit, query.offset)
    return result


async def get_contract_by_id(session, id, manager_id):
    stmt = (
        select(Contract)
        .options(selectinload(Contract.company).selectinload(Company.client))
        .options(selectinload(Contract.branch))
        .join(Contract.company)
        .join(Company.client)
        .where(Contract.id == id)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_contract(session, data):
    contract = Contract(
        number=data.number,
        status=data.status,
        name=data.name,
        description=data.description,
        valid_from=data.valid_from,
        valid_to=data.valid_to,
        company_id=data.company_id,
        branch_id=data.branch_id,
    )

    session.add(contract)
    await session.flush()
    return contract
