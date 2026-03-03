from app.database.company import (
    get_filtered_companies,
    get_company_by_id,
    get_company_by_inn,
    add_company,
)
from app.database.client import get_client_by_id
from app.config.config import ApplicationException
from app.schemas.company import CompanyItem
from app.schemas.common import to_schema
from .common import Access


async def get_company_list(session, roles, requester_id, scope, client_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id_with_scope(
        user_id=requester_id, 
        scope=scope
    )

    companies = await get_filtered_companies(session, manager_id, client_id)

    if not companies:
        raise ApplicationException("Companies Not Found", 404)

    return companies


async def get_company(session, roles, requester_id, company_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

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
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)
    
    company = await get_company_by_id(session, manager_id, company_id)

    if not company:
        raise ApplicationException("Company Not found", 404)

    if company.is_archived is False:
        raise ApplicationException("Company is already active", 400)

    company.is_archived = False
    return company
