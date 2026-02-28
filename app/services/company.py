from app.database.company import get_filtered_companies, get_company_by_id, get_company_by_inn, add_company
from app.database.client import get_client_by_id
from app.config.config import ApplicationException
from app.schemas.company import CompanyItem
from app.schemas.base import to_schema

async def get_company_list(session, roles, requester_id, scope, client_id): 
    is_admin = {"owner", "admin"}.intersection(roles)
    is_manager = "manager" in roles

    if not (is_admin or is_manager):
        raise ApplicationException(f"Cannot access company with roles {roles}", 403)
    
    manager_id = None
    if is_manager and (scope == "mine" or not is_admin):
        manager_id = requester_id

    companies = await get_filtered_companies(
        session,
        manager_id,
        client_id
    )

    if not companies:
        raise ApplicationException("Companies Not Found", 404) 
        
    return companies

async def get_company(session, requester_roles, requester_id, company_id):
    is_admin = {"owner", "admin"}.intersection(requester_roles)
    is_manager = "manager" in requester_roles
    
    if not (is_admin or is_manager):
        raise ApplicationException(
            f"Cannot access company with roles {requester_roles}", 
            403
        )
    
    manager_id = None
    if is_manager and not is_admin:
        manager_id = requester_id

    company = await get_company_by_id(session, manager_id, company_id)
    if not company:
        raise ApplicationException("Company Not Found", 404) 

    if company.is_archived:
        raise ApplicationException("Company is deleted", 400)

    return to_schema(CompanyItem, company)


async def create_company(session, data, manager_id):
    company = await get_company_by_inn(session, data.inn)  
    if company:
        if company.is_archived:
            raise ApplicationException(f"Company with inn {data.inn} is archived", 400)
        
        raise ApplicationException(f"Company with inn {data.inn} already exists", 400)

    client = await get_client_by_id(session, data.client_id, manager_id)
    if not client:
        raise ApplicationException(f"Client Not Found or Client Access Forbidden ", 404) 
    
    new_company = await add_company(session, data)
    
    return new_company


async def archive_company(session, company_id, manager_id):
    company = await get_company_by_id(session, manager_id, company_id)

    if not company:
        raise ApplicationException("Company Not found", 404)

    if company.is_archived:
        raise ApplicationException("Company is already archived", 400)

    company.is_archived = True
    return company


async def restore_company(session, company_id, roles, requester_id):
    is_admin = bool({"owner", "admin"}.intersection(roles))

    if "manager" not in roles and not is_admin:
        raise ApplicationException(
            f"Cannot access company with roles {roles}",
            403
        )
    
    manager_id = None if is_admin else requester_id
    company = await get_company_by_id(session, manager_id, company_id)

    if not company:
        raise ApplicationException("Company Not found", 404)

    if company.is_archived is False:
        raise ApplicationException("Company is already active", 400)

    company.is_archived = False
    return company
