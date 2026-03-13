from app.database.contract import (
    get_filtered_contracts,
    get_contract_by_id,
    add_contract,
)
from app.database.branch import get_branch_by_id
from app.database.company import get_company_by_id
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.contract import GetContractItem
from .common import Access


async def get_contract_list(session, roles, requester_id, query):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id_with_scope(user_id=requester_id, scope=query.scope)

    contracts = await get_filtered_contracts(
        session=session, manager_id=manager_id, query=query
    )

    if not contracts:
        raise ApplicationException("contracts Not Found", 404)

    return {
        "items": contracts.items,
        "total": contracts.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_contract(session, roles, requester_id, contract_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    contract = await get_contract_by_id(session, contract_id, manager_id)
    if not contract:
        raise ApplicationException("Contract Not Found", 404)

    if contract.is_archived:
        raise ApplicationException("contract is deleted", 400)

    return to_schema(GetContractItem, contract)


async def change_contract(session, roles, user_id, contract_id, item):
    manager_id = Access(roles).manager_id(user_id)

    contract = await get_contract_by_id(session, contract_id, manager_id)
    if not contract:
        raise ApplicationException("Contract Not found", 404)

    if contract.is_archived:
        raise ApplicationException(f"A contract '{contract.name}' is archived", 400)

    update_data = item.model_dump(exclude_unset=True)

    start_date = update_data.get("valid_from", None) or contract.valid_from
    end_date = update_data.get("valid_to", None) or contract.valid_to

    if start_date > end_date:
        raise ApplicationException("End-date cannot be less than start-date", 400)

    for name, value in update_data.items():
        setattr(contract, name, value)

    return to_schema(GetContractItem, contract)


async def create_contract(session, data, manager_id):
    company = await get_company_by_id(session, manager_id, data.company_id)
    if not company:
        raise ApplicationException("Company Not Found ", 404)

    branch = await get_branch_by_id(session, data.branch_id)
    if not branch:
        raise ApplicationException("Branch Not Found ", 404)

    if data.valid_from > data.valid_to:
        raise ApplicationException("End-date cannot be less than start-date", 400)

    contract = await add_contract(session, data)

    return contract


async def archive_contract(session, contract_id, manager_id):
    contract = await get_contract_by_id(session, contract_id, manager_id)

    if not contract:
        raise ApplicationException("contract Not found", 404)

    if contract.is_archived:
        raise ApplicationException("contract is already archived", 400)

    contract.is_archived = True
    return contract


async def restore_contract(session, contract_id, roles, requester_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    contract = await get_contract_by_id(session, contract_id, manager_id)

    if not contract:
        raise ApplicationException("contract Not found", 404)

    if contract.is_archived is False:
        raise ApplicationException("contract is already active", 400)

    contract.is_archived = False
    return contract
