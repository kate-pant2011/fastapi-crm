from app.config.config import ApplicationException
from app.database.generated_doc import get_all_generated_docs, get_generated_doc_by_id
from app.schemas.generated_doc import GeneratedListResponse, GeneratedItem
from app.email.service import send_email_service
from dataclasses import dataclass
import asyncio
from pathlib import Path
from app.file_handler import FileUploadDTO, FileNameDTO
from app.database.generated_doc import add_generated_doc
from app.database.file import add_file, get_file_by_unique_name
import os

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


async def convert_word_to_pdf(
          session,
          user_id,
          generated_doc_id
):
    document = await get_generated_doc_by_id(session, generated_doc_id)

    if not document:
        raise ApplicationException("Document Not Found", 404)
    
    if document.creator_id != user_id:
        raise ApplicationException("Access to the document denied", 403)
    
    if "word" not in document.file.mime_type:
        raise ApplicationException(
            "Only DOCX files can be converted to PDF",
            400,
        )
    
    path = document.file.path
    output_dir = "./uploads"

    process = await asyncio.create_subprocess_exec(
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        path,
        "--outdir",
        output_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    return_code = await process.wait()

    if return_code != 0:
        raise ApplicationException(
            "PDF generation failed",
            500,
        )

    pdf_path = (
        Path(output_dir)
        / f"{Path(path).stem}.pdf"
    )

    if not pdf_path.exists():
        raise ApplicationException(
            "PDF generation failed",
            500,
        )

    size = os.path.getsize(pdf_path)
    unique_name = Path(document.file.unique_name).with_suffix(".pdf").name
    original_name = Path( document.file.name).with_suffix(".pdf").name


    pdf_file = await get_file_by_unique_name(
        session,
        unique_name,
    )
    if pdf_file:
        pdf_file.size = size
        pdf_file.path = str(pdf_path)
        pdf_file.name = original_name
        pdf_file.unique_name = unique_name

        generated_pdf = pdf_file.generated_document
        
    else:
        data = FileUploadDTO(
            filenames=FileNameDTO(
                original=original_name,
                unique=unique_name
            ),
            path=str(pdf_path),
            size=size,
            mime_type="application/pdf"
        )

        pdf_file = await add_file(session, data, user_id) 

        if document.template_id:
            pdf_file.template_id = document.template_id

        generated_pdf = await add_generated_doc(session, document.template_id, user_id, pdf_file.id)


    return {
        "doc_id": generated_pdf.id, 
        "file_id": pdf_file.id, 
        "filename": pdf_file.name,
    }