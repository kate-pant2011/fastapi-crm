import os
import aiofiles
from fastapi import UploadFile
import uuid
import magic
from app.config.config import ApplicationException
from dataclasses import dataclass

@dataclass 
class FileNameDTO:
    original: str
    unique: str

@dataclass 
class FileUploadDTO:
    filenames: FileNameDTO
    path: str
    size: int
    mime_type: str

ALLOWED_MIME = {
    "png": ["image/png"],
    "jpg": ["image/jpeg"],
    "jpeg": ["image/jpeg"],
    "webp": ["image/webp"],
    "gif": ["image/gif"],

    "pdf": ["application/pdf"],

    "html": ["text/html"],
    "htm": ["text/html"],

    "txt": ["text/plain"],

    "json": ["application/json", "text/plain"],
    "xml": ["application/xml", "text/xml"],

    "doc": ["application/msword"],

    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",  
    ],

    "xls": ["application/vnd.ms-excel"],

    "xlsx": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
    ],

    "ppt": ["application/vnd.ms-powerpoint"],

    "pptx": [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/zip",
    ],

    "zip": ["application/zip"],
}


class FileHandler:
    def __init__(self, folder="./uploads"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    async def upload_file(self, file: UploadFile):
        ext = file.filename.split(".")[-1].lower()
        filenames = self.get_file_name(file, ext)

        file_path = os.path.join(self.folder, filenames.unique)

        max_size = 30 * 1024 * 1024
        size = 0

        first_chunk = True

        async with aiofiles.open(file_path, "wb") as f:
            while chunk:= await file.read(1024 * 1024):
                if first_chunk:
                    try:
                        mime_type = self.check_mime(chunk, ext)
                    except ApplicationException as e:
                        await f.close()
                        if os.path.exists(file_path):
                            
                            os.remove(file_path)
                        raise  
                    first_chunk = False

                size += len(chunk)

                if size > max_size:
                    await f.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise ApplicationException(400, "Файл слишком большой")
                 
                await f.write(chunk)

        if size == 0:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ApplicationException("Файл пуст", 400)
        
        return FileUploadDTO(
            filenames=filenames,
            path=file_path,
            size=size, 
            mime_type=mime_type
        )

    def delete_file(self, path: str):
        if os.path.exists(path):
            os.remove(path)
            return True
        
        return False
    
    def check_mime(self, chunk, ext):
        file_mime = magic.from_buffer(chunk[:2048], mime=True)

        if file_mime not in ALLOWED_MIME[ext]:
            raise ApplicationException(400, f"Неверный mime тип '{file_mime}' для расширения {ext}")
        
        return file_mime
    
    def get_file_name(self, file, ext):
        filename = os.path.basename(file.filename or "") or "unknown"
        unique_name = f"{uuid.uuid4().hex[:30]}.{ext}"

        return FileNameDTO(
            original = filename,
            unique = unique_name
        )

    async def validate_file(self, file: UploadFile, max_size: int = 30 * 1024 * 1024):
        size = 0
        first_chunk = True
        mime_type = None
        ext = file.filename.split(".")[-1].lower()

        chunks = []

        while chunk := await file.read(1024 * 1024):
            if first_chunk:
                mime_type = self.check_mime(chunk, ext)
                first_chunk = False

            size += len(chunk)

            if size > max_size:
                raise ApplicationException(400, "Файл слишком большой")
            
            chunks.append(chunk)
        
        content = b"".join(chunks)

        await file.seek(0)  

        return {
            "filename": file.filename or "unknown",
            "size": size,
            "content_type": file.content_type,
            "content": content 
        }