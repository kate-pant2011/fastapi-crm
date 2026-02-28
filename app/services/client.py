from app.database.client import (
    get_filtered_clients,
    add_client,
    get_client_by_name,
    get_client_by_id,
)
from app.config.config import ApplicationException
from app.schemas.base import to_schema
from app.schemas.client import ClientItem


async def form_client_list(session, requester_roles, requester_id, scope): 
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))
    is_manager = "manager" in requester_roles

    if not (is_admin or is_manager):
        raise ApplicationException(
            f"Cannot access client with roles {requester_roles}",
            403
        )

    manager_id = None
    if is_manager and (scope == "mine" or not is_admin):
        manager_id = requester_id

    clients = await get_filtered_clients(session, manager_id)

    if not clients:
        raise ApplicationException("Clients Not found", 404)
    
    return clients


async def get_client(session, requester_roles, requester_id, client_id):
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))
    is_manager = "manager" in requester_roles

    if not (is_manager or is_admin):
        raise ApplicationException(
            f"Cannot access client with roles {requester_roles}",
            403
        )

    manager_id = None
    if is_manager and not is_admin:
        manager_id = requester_id

    client = await get_client_by_id(session, client_id, manager_id)

    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived:
        raise ApplicationException("Client is archived", 400)
    
    return to_schema(ClientItem, client)

async def create_client(session, data, manager_id):
    client = await get_client_by_name(session, data.name)

    if client:
        if client.is_archived:
            raise ApplicationException(
                f"Client named {data.name} is archived", 400, {"id": client.id}
            )

        raise ApplicationException(f"Client named {data.name} already exists", 400)

    new_client = await add_client(session, data, manager_id)
    return new_client


async def archive_client(session, client_id, manager_id):
    client = await get_client_by_id(session, client_id, manager_id)

    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived:
        raise ApplicationException("Client is already archived", 400)

    client.is_archived = True
    return client


async def restore_client(session, client_id, requester_roles, requester_id):
    is_admin = bool({"owner", "admin"}.intersection(requester_roles))

    if "manager" not in requester_roles and not is_admin:
        raise ApplicationException(
            f"Cannot access client with roles {requester_roles}",
            403
        )
    
    manager_id = None if is_admin else requester_id
    client = await get_client_by_id(session, client_id, manager_id)

    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived is False:
        raise ApplicationException("Client is already active", 400)

    client.is_archived = False
    return client
