import logging

document_logger = logging.getLogger("audit.documents")
file_logger = logging.getLogger("audit.files")

class DocsAudit:
    def __init__(self):
        self.logger = document_logger
    
    def document_generated(self, user_id, file_id, file_name, template_id):
        self.logger.info(
            "User generated document",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "template_id": template_id,
                "file_type": "word"
            }
        )

    def document_exported_pdf(self, user_id, file_id, file_name, template_id):
        self.logger.info(
            "User converted document to pdf",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "template_id": template_id,
                "file_type": "pdf"
            }
        )

    def document_access_denied(self, user_id, document_id, document_name):
        self.logger.warning(
            "Access to document denied",
            extra={
                "user_id": user_id, 
                "document_id": document_id, 
                "document_name": document_name
            }
        )

    def template_created(self, user_id, template_id, template_name):
        self.logger.info(
            "User created template",
            extra={
                "user_id": user_id, 
                "template_id": template_id, 
                "template_name": template_name
            }
        )

    def template_updated(self, user_id, template_id, template_name):
        self.logger.info(
            "User updated template",
            extra={
                "user_id": user_id, 
                "template_id": template_id, 
                "template_name": template_name
            }
        )

    def template_access_denied(self, user_id, template_id, template_name, reason):
        self.logger.warning(
            "Access to template denied",
            extra={
                "user_id": user_id, 
                "template_id": template_id, 
                "template_name": template_name,
                "reason": reason
            }
        )

docs_audit = DocsAudit()

class FileAudit:
    def __init__(self):
        self.logger = file_logger

    def file_uploaded(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.info(
            "User uploaded file",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": "uploaded"
            }
        )
    

    def file_downloaded(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.info(
            "User downloaded file",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": "downloaded"
            }
        )

    def file_deleted(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.info(
            "User deleted file",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": "deleted"
            }
        )

    def file_access_denied(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.warning(
            "Access to file denied",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        )

    def file_delete_denied(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.warning(
            "Access to delete file denied",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        )

    def file_download_denied(
            self, user_id, file_id, file_name, entity_type, entity_id
    ):
        self.logger.warning(
            "Access to download file denied",
            extra={
                "user_id": user_id,
                "file_id": file_id,
                "file_name": file_name,
                "entity_type": entity_type,
                "entity_id": entity_id,

            }
        )

file_audit = FileAudit()