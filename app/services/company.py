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

sorting_rules = {"inn": ("inn",), "name": ("name",)}

async def get_company_list(session, roles, requester_id, query):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id_with_scope(user_id=requester_id, scope=query.scope)

    companies = await get_filtered_companies(
        session=session, manager_id=manager_id, query=query, sorting_rules=sorting_rules
    )

    return {
        "items": companies.items or [],
        "total": companies.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_company(session, roles, requester_id, company_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    company = await get_company_by_id(session, company_id, manager_id)
    if not company:
        raise ApplicationException("Company Not Found", 404)

    if company.is_archived:
        raise ApplicationException("Company is archived", 400, {"id": company.id})

    return to_schema(CompanyItem, company)


async def change_company(session, roles, user_id, company_id, item):
    manager_id = Access(roles).manager_id(user_id)

    company = await get_company_by_id(session, company_id,  manager_id)
    if not company:
        raise ApplicationException("Company Not found", 404)

    if company.is_archived:
        raise ApplicationException(f"A company '{company.name}' is archived", 400, {"id": company.id})

    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():
        setattr(company, name, value)

    return to_schema(CompanyItem, company)


async def create_company(session, data, manager_id):
    company = await get_company_by_inn(session, data.inn)
    if company:
        if company.is_archived:
            raise ApplicationException(f"Company with inn {data.inn} is archived", 400, {"id": company.id})

        raise ApplicationException(f"Company with inn {data.inn} already exists", 400)

    client = await get_client_by_id(session, data.client_id, manager_id)
    if not client:
        raise ApplicationException("Client Not Found or Client Access Forbidden ", 404)

    new_company = await add_company(session, data)

    return new_company


async def archive_company(session, company_id, manager_id):
    company = await get_company_by_id(session, company_id, manager_id)

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

    company = await get_company_by_id(session, company_id, manager_id)

    if not company:
        raise ApplicationException("Company Not found", 404)

    if company.is_archived is False:
        raise ApplicationException("Company is already active", 400)

    company.is_archived = False
    return company
