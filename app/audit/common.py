import logging

common_logger = logging.getLogger("audit.common")


class Audit:
    def __init__(self):
        self.logger = common_logger  

    def access_denied(self, user_id, entity_id, entity_name):
        self.logger.warning(
            "Access denied",
            extra={
                "user_id": user_id, 
                "entity_id": entity_id,
                "entity_name": entity_name
            }
        )

audit = Audit()