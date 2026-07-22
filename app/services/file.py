from app.database.file import add_file, get_file_by_id, get_all_files
from app.file_handler import FileHandler
from app.config.config import ApplicationException
from app.schemas.file import FileItem
from app.database.project import get_project_by_id
from app.database.client import get_client_by_id
from app.database.branch import get_branch_by_id_with_stamp, get_branch_by_id
from app.schemas.common import to_schema
from app.audit.documents import file_audit
from .common import Access
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

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

    elif file.template_id:
        if file.creator_id != user_id:
            raise ApplicationException("Access denied", 403)
    
    else:
        file_audit.file_access_denied(
            user_id=user_id, 
            file_id=file.id,
            file_name=file.name,
            entity_type=None, 
            entity_id=None
        )
        raise ApplicationException("Access denied", 403)


async def check_roles_and_entity(session, user_id, roles, entity_type, entity_id):
    access = Access(roles)
    is_admin = access.is_admin()
    
    if not is_admin:
        manager_id = access.manager_id(user_id)
        executor_id = access.executor_id(user_id)
    else:
        manager_id, executor_id = None, None

    if entity_type not in ("client", "project", "branch"):
        raise ApplicationException("File location Not Found", 400)

    if entity_type == "project":
        entity = await get_project_by_id(session, entity_id, manager_id, executor_id)

    elif entity_type == "client":
        entity = await get_client_by_id(session, entity_id, manager_id)

    elif entity_type == "branch":
        entity = await get_branch_by_id(session, entity_id)

    if not entity: 
        raise ApplicationException(f"{entity_type} not found", 404)


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
            
            elif entity_type == "branch":
                branch = await get_branch_by_id_with_stamp(session, entity_id)
                branch.stamp_file_id = added_file.id

            added_files.append(added_file)

            file_audit.file_uploaded(
                user_id=user_id, 
                file_id=added_file.id, 
                file_name=added_file.name, 
                entity_type=entity_type, 
                entity_id=entity_id
            )

        except ApplicationException:
            for path in saved_paths:
                handler.delete_file(path)

            raise

        except Exception as e:
            for path in saved_paths:
                handler.delete_file(path)

            logger.exception(
                "File upload failed: entity_type=%s entity_id=%s", 
                entity_type, 
                entity_id
            )
            raise ApplicationException(f"{type(e).__name__}", 500)
    
    return added_files 


async def get_file_for_download(session, user_id, roles, file_id):
    file = await get_file_by_id(session, file_id)

    if not file:
        raise ApplicationException("File not found", 404)

    entity_id, entity_type = await get_entity(file)

    if entity_type not in ["branch", "template"]:
        await check_files_access(file, session, user_id, roles)
    
    file_audit.file_downloaded(
        user_id=user_id, 
        file_id=file.id, 
        file_name=file.name, 
        entity_type=entity_type, 
        entity_id=entity_id
    )

    return file


async def delete_file(session, user_id, roles, file_id):
    file = await get_file_by_id(session, file_id)
    
    if not file:
        raise ApplicationException("File not found", 404)


    entity_id, entity_type = await get_entity(file)

    if entity_type not in ["branch", "template"]:
        await check_files_access(file, session, user_id, roles)

    handler = FileHandler()
    handler.delete_file(file.path)

    await session.delete(file)

    file_audit.file_deleted(
        user_id=user_id, 
        file_id=file.id, 
        file_name=file.name, 
        entity_type=entity_type, 
        entity_id=entity_id
    )
    return True

async def get_entity(file):
    if file.client_id is not None:
        return file.client_id, "client"
    
    elif file.project_id is not None:
        return file.project_id, "project"
    
    elif file.template_id is not None:
        return file.template_id, "template"
    
    else:
        return None, "branch" 
    # по умолчанию все, что не относится к client, project, template, относится к branch
