from app.database.client import (
    get_filtered_clients,
    add_client,
    get_client_by_name,
    get_client_by_id,
)
from app.config.config import ApplicationException
from app.schemas.common import to_schema
from app.schemas.client import ClientItem
from .common import Access


async def form_client_list(session, roles, requester_id, query):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id_with_scope(
        user_id=requester_id, 
        scope=query.scope,
        manager_id=query.manager_id
    )    
      
    clients = await get_filtered_clients(session, manager_id, query)

    if not clients:
        raise ApplicationException("Clients Not found", 404)

    return {"items": clients.items, "total": clients.total, "limit": query.limit, "offset": query.offset}


async def get_client(session, roles, requester_id, client_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    client = await get_client_by_id(session, client_id, manager_id)

    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived:
        raise ApplicationException("Client is archived", 400)

    return to_schema(ClientItem, client)

async def change_client(session, roles, user_id, client_id, item):
    manager_id = Access(roles).manager_id(user_id)
    
    client = await get_client_by_id(session, client_id, manager_id)
    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived:
        raise ApplicationException(f"A client '{client.name}' is archived", 400)
    
    update_data = item.model_dump(exclude_unset=True)

    for name, value in update_data.items():   
        setattr(client, name, value)

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


async def restore_client(session, client_id, roles, requester_id):
    access = Access(roles)
    access.require_admin_or_manager()
    manager_id = access.manager_id(requester_id)

    client = await get_client_by_id(session, client_id, manager_id)

    if not client:
        raise ApplicationException("Client Not found", 404)

    if client.is_archived is False:
        raise ApplicationException("Client is already active", 400)

    client.is_archived = False
    return client
