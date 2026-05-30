from app.database.file import add_file, get_file_by_id, get_all_files
from app.file_handler import FileHandler
from app.config.config import ApplicationException
from app.schemas.file import FileItem
from app.database.project import get_project_by_id
from app.database.client import get_client_by_id
from app.schemas.common import to_schema
from .common import Access
from dataclasses import dataclass

@dataclass
class FileDTO:
    name: str
    mime_type: str

sorting_rules = {"name": ("name","created_at")}


async def check_files_access(file, session, user_id, roles):
    if file.project_id:
        entity_type = "project"
        entity_id = file.project_id
        await check_roles_and_entity(session, user_id, roles, entity_type, entity_id)

    elif file.client_id:
        entity_type = "client"
        entity_id = file.client_id
        await check_roles_and_entity(session, user_id, roles, entity_type, entity_id)

    elif file.generated_document:
        if file.creator_id != user_id:
            raise ApplicationException("Access denied", 403)
    


async def check_roles_and_entity(session, user_id, roles, entity_type, entity_id):
    access = Access(roles)
    manager_id = access.manager_id(user_id)
    executor_id = access.executor_id(user_id)
    is_admin = access.is_admin()

    if entity_type not in ("client", "project"):
        raise ApplicationException("File location Not Found", 400)

    if entity_type == "project":
        entity = await get_project_by_id(session, entity_id, manager_id, executor_id)

    elif entity_type == "client":
        entity = await get_client_by_id(session, entity_id, manager_id)

    if not entity: 
        if not is_admin:
            raise ApplicationException(f"{entity_type} not found", 404)
        return

    if entity.is_archived:
        raise ApplicationException(f"{entity_type} is archived", 400)


async def get_file_list(session, user_id, roles, entity_id, entity_type, query):
    await check_roles_and_entity(session, user_id, roles, entity_type, entity_id)

    files = await get_all_files(session, query, entity_id, entity_type, sorting_rules)

    return {
        "items": files.items,
        "total": files.total,
        "limit": query.limit,
        "offset": query.offset,
    }


async def get_file(session, user_id, roles, file_id):
    file = await get_file_by_id(session, file_id)

    if not file:
        raise ApplicationException("File not found", 404)
    
    await check_files_access(file, session, user_id, roles)

    return to_schema(FileItem, file)


async def upload_file(session, user_id, roles, files, entity_id, entity_type: str):
    if entity_type != "template":
        await check_roles_and_entity(session, user_id, roles, entity_type, entity_id)

    added_files = []
    saved_paths = []
    handler = FileHandler()

    for file in files: 
        try:
            uploaded_file = await handler.upload_file(file)
            saved_paths.append(uploaded_file.path)

            added_file = await add_file(session, uploaded_file, user_id)

            if entity_type == "project":
                added_file.project_id = entity_id

            elif entity_type == "client":
                added_file.client_id = entity_id    
            
            elif entity_type == "template":
                added_file.template_id = entity_id

            added_files.append(added_file)

        except Exception as e:
            for path in saved_paths:
                handler.delete_file(path)

            raise ApplicationException(f"{type(e).__name__} - {e}", 500)

    return added_files 


async def get_file_for_download(session, user_id, roles, file_id):
    file = await get_file_by_id(session, file_id)

    if not file:
        raise ApplicationException("File not found", 404)


    await check_files_access(file, session, user_id, roles)

    return file


async def delete_file(session, user_id, roles, file_id):
    file = await get_file_by_id(session, file_id)
    
    if not file:
        raise ApplicationException("File not found", 404)
    
    await check_files_access(file, session, user_id, roles)

    handler = FileHandler()
    handler.delete_file(file.path)

    await session.delete(file)

    return True