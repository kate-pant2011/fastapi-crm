from app.config.config import ApplicationException
from app.database.generated_doc import get_all_generated_docs, get_generated_doc_by_id
from app.schemas.generated_doc import GeneratedListResponse, GeneratedItem
from app.email.service import send_email_service
from dataclasses import dataclass

async def get_generated_docs(session, user_id, query):

    docs = await get_all_generated_docs(session, user_id, query)

    result = []
    for d in docs.items:
        result.append(
            GeneratedItem(
                id=d.id,
                file_id=d.file_id,
                template_id=d.template_id,
                creator_id=d.creator_id,
                filename=d.file.name,
            )
        )

    return GeneratedListResponse(
        items=result,
        total= docs.total,
        limit=query.limit,
        offset=query.offset,
    )

@dataclass
class FileValidateDTO:
    filename: str
    mime_type: str
    size: int
    content: bytes | None = None
    path: str | None = None


async def send_generated_doc(
          session,
          user_id,
          generated_doc_id,
          item
):
    document = await get_generated_doc_by_id(session, generated_doc_id)

    if not document:
        raise ApplicationException("Document Not Found", 404)
    
    if document.creator_id != user_id:
        raise ApplicationException("Access to the document denied", 403)
    
    files = FileValidateDTO(
        filename = document.file.name,
        mime_type = document.file.mime_type,
        size = document.file.size,
        content = None,
        path = document.file.path
    )

    await send_email_service(
        session,
        [files], 
        item.email_id, 
        item.to, 
        item.cc, 
        item.bcc, 
        item.subject, 
        item.body, 
        user_id
    )

    return {"status": "sent"}