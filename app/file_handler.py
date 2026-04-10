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

ALLOWED_EXT = {
    "png", "jpg", "jpeg", "webp", 
    "gif", "pdf", "html", "doc", 
    "docx","xls", "xlsx","ppt", 
    "pptx", "txt", "json","xml", 
    "htm","zip"
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
                    mime_type = self.check_mime(chunk, ext)
                    first_chunk = False

                size += len(chunk)

                if size > max_size:
                    raise ApplicationException(400, "File too big")
                 
                await f.write(chunk)

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
        if ext not in ALLOWED_EXT:
            raise ApplicationException(400, f"Extension {ext} not allowed")
        
        file_mime = magic.from_buffer(chunk[:2048], mime=True)
        
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

        while chunk := await file.read(1024 * 1024):
            if first_chunk:
                mime_type = self.check_mime(chunk, ext)
                first_chunk = False

            size += len(chunk)

            if size > max_size:
                raise ApplicationException(400, "File too big")

        await file.seek(0)  

        return {
            "filename": file.filename or "unknown",
            "size": size,
            "content_type": file.content_type,
        }