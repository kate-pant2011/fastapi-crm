from app.database.contract import get_filtered_contracts, get_contract_by_id, get_contract_by_number, add_contract
from app.database.branch import get_branch_by_id
from app.database.company import get_company_by_id
from app.config.config import ApplicationException
from app.schemas.base import to_schema
from app.schemas.contract import GetcontractItem


async def get_contract_list(session, roles, requester_id, scope, client_id): 
    is_admin = {"owner", "admin"}.intersection(roles)
    is_manager = "manager" in roles

    if not (is_admin or is_manager):
        raise ApplicationException(
            f"Cannot access contract with roles {roles}", 
            403
        )
    
    manager_id = None
    if is_manager and (scope == "mine" or not is_admin):
        manager_id = requester_id

    contracts = await get_filtered_contracts(
        session,
        client_id,
        manager_id,
    )

    if not contracts:
        raise ApplicationException("contracts Not Found", 404) 
        
    return contracts


async def get_contract(session, roles, requester_id, contract_id, client_id):
    is_admin = {"owner", "admin"}.intersection(roles)
    is_manager = "manager" in roles
    
    if not (is_admin or is_manager):
        raise ApplicationException(
            f"Cannot access contract with roles {roles}", 
            403
        )
    
    manager_id = None
    if is_manager and not is_admin:
        manager_id = requester_id

    contract = await get_contract_by_id(session, contract_id,  manager_id, client_id)
    if not contract:
        raise ApplicationException("Contract Not Found", 404) 

    if contract.is_archived:
        raise ApplicationException("contract is deleted", 400)

    return to_schema(GetcontractItem, contract)


async def create_contract(session, data, manager_id):
    company = await get_company_by_id(session, data.company_id, manager_id)
    if not company:
        raise ApplicationException(f"Company Not Found ", 404) 
    
    branch = await get_branch_by_id(session, data.branch_id)    
    if not branch:
        raise ApplicationException(f"Branch Not Found ", 404) 
    
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


async def restore_contract(session, contract_id, requester_roles, requester_id):
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))

    if "manager" not in requester_roles and not is_admin:
        raise ApplicationException(
            f"Cannot access contract with roles {requester_roles}",
            403
        )
    
    manager_id = None if is_admin else requester_id
    contract = await get_contract_by_id(session, contract_id, manager_id)

    if not contract:
        raise ApplicationException("contract Not found", 404)

    if contract.is_archived is False:
        raise ApplicationException("contract is already active", 400)

    contract.is_archived = False
    return contract