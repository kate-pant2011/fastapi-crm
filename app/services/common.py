from app.config.config import ApplicationException

ROLES = ["owner", "admin", "manager", "executor"]


class Access:
    ADMIN_ROLES = {"owner", "admin"}

    def __init__(self, roles):
        self.roles = roles

    def is_owner(self):
        return "owner" in self.roles

    def is_admin(self):
        return bool(self.ADMIN_ROLES.intersection(self.roles))

    def is_manager(self):
        return "manager" in self.roles

    def is_executor(self):
        return "executor" in self.roles

    def require_admin_or_manager(self):
        if not (self.is_admin() or self.is_manager()):
            raise ApplicationException(
                f"Cannot access client with roles {self.roles}", 403
            )

    def executor_id(self, user_id):
        if self.is_executor() and not self.is_admin():
            return user_id

        return None

    def manager_id(self, user_id):
        if self.is_manager() and not self.is_admin():
            return user_id

        return None

    def manager_id_with_scope(self, user_id, scope, manager_id=None):
        if manager_id and self.is_admin():
            return manager_id

        elif self.is_manager() and (scope == "mine" or not self.is_admin()):
            return user_id

        return None
