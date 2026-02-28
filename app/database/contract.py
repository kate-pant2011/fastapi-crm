from sqlalchemy import select
from app.models.contract import Contract
from app.models.client import Client
from app.models.company import Company
from sqlalchemy.orm import selectinload


async def get_filtered_contracts(session, client_id,  manager_id):
    stmt = (
        select(Contract)
        .join(Contract.company)
        .join(Company.client)
        .where(Contract.is_archived == False)
    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)
   
    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)
    
    result = await session.execute(stmt)
    return result.scalars().all()
    

async def get_contract_by_id(session, id, manager_id, client_id=None):
    stmt = (
        select(Contract)
        .options(selectinload(Contract.company))
        .options(selectinload(Contract.branch))
        .join(Contract.company)
        .join(Company.client)
        .where(Contract.id == id)
        .where(Contract.is_archived == False)

    )

    if manager_id is not None:
        stmt = stmt.where(Client.manager_id == manager_id)
    
    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_contract_by_number(session, number: str):
    result = await session.execute(
        select(Contract)
        .where(Contract.number == number)
    )

    return result.scalar_one_or_none()

async def add_contract(session, data):
    contract = Contract(
        number = data.number,
        status = data.status,
        name = data.name,
        description = data.description,
        valid_from = data.valid_from,
        valid_to = data.valid_to,
        company_id=data.company_id,
        branch_id=data.branch_id
    )

    session.add(contract)
    await session.flush()
    return contract