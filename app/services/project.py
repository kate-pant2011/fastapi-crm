from app.config.config import ApplicationException
from app.database.contract import get_contract_by_id
from app.database.client import get_client_by_id
from app.database.user import get_user_by_id
from app.database.project import (
    get_filtered_projects,
    add_project,
    get_project_by_name,
    get_project_by_id,

)
from app.schemas.base import to_schema, ShortItem
from app.schemas.contract import ContractItem


async def get_project_list(
        session, requester_roles, requester_id, scope, client_id
): 
    is_admin = {"owner", "admin"}.intersection(requester_roles)
    is_manager = "manager" in requester_roles

    if not (is_admin or is_manager):
        raise ApplicationException(
            f"Cannot access contract with roles {requester_roles}", 
            403
        )
    
    manager_id = None
    if is_manager and (scope == "mine" or not is_admin):
        manager_id = requester_id

    contracts = await get_filtered_projects(
        session,
        manager_id,
        client_id
    )

    if not contracts:
        raise ApplicationException("contracts Not Found", 404) 
        
    return contracts


async def get_project(session, requester_roles, requester_id, project_id):
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))
    is_manager = "manager" in requester_roles

    if not is_manager and not is_admin:
        raise ApplicationException(
            f"Cannot access project with roles {requester_roles}",
            403
        )

    manager_id = None
    if not is_admin:
        manager_id = requester_id

    project = await get_project_by_id(session, project_id, manager_id)
    if not project:
        raise ApplicationException("project Not found", 404)

    if project.is_archived:
        raise ApplicationException("project is deleted", 400)
    
    manager = await get_user_by_id(session, project.client.manager_id)
    if not manager:
        raise ApplicationException("manager Not found", 404)
    
    return {
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "client_name": project.client.name,
        "client_email": project.client.email,
        "contract": to_schema(ContractItem, project.contract) if project.contract else None,
        "manager": to_schema(ShortItem, manager),
        "stages": [to_schema(ShortItem, stage) for stage in project.stages]
    }

async def create_project(session, data, manager_id):
    project = await get_project_by_name(session, data.name)

    if project:
        if project.is_archived:
            raise ApplicationException(
                f"Project  named {data.name} is archived", 400, {"id": project.id}
            )

        raise ApplicationException(f"Project named {data.name} already exists", 400)

    client = await get_client_by_id(session, data.client_id, manager_id)
    if not client:
        raise ApplicationException("client Not found", 404)

    if client.is_archived:
        raise ApplicationException("project is deleted", 400)

    if data.contract_id:
        contract = await get_contract_by_id(session, data.contract_id, manager_id, client.id)
        if not contract:
            raise ApplicationException("contract Not found", 404)

        if contract.is_archived:
            raise ApplicationException("project is deleted", 400)
    
    new_project = await add_project(session, data)

    return new_project

async def archive_project(session, project_id, manager_id):
    project = await get_project_by_id(session, project_id, manager_id)

    if not project:
        raise ApplicationException("project Not found", 404)

    if project.is_archived:
        raise ApplicationException("project is already archived", 400)

    project.is_archived = True
    return project


async def restore_project(session, project_id, requester_roles, requester_id):
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))

    if "manager" not in requester_roles and not is_admin:
        raise ApplicationException(
            f"Cannot access project with roles {requester_roles}",
            403
        )
    
    manager_id = None if is_admin else requester_id
    project = await get_project_by_id(session, project_id, manager_id)

    if not project:
        raise ApplicationException("project Not found", 404)

    if project.is_archived is False:
        raise ApplicationException("project is already active", 400)

    project.is_archived = False
    return project
