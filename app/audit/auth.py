import logging

auth_logger = logging.getLogger("audit.auth")


class AuthAudit:
    def __init__(self):
        self.logger = auth_logger

    def signup_success(self, user_email, ip):
        self.logger.info(
            "User signed up successfully",
            extra={"user_email": self._mask_email(user_email), "ip": ip}
        )

    def login_success(self, user_email, ip, device):
        self.logger.info(
            "User logged in successfully",
            extra={"user_email": self._mask_email(user_email), "ip": ip, "device": device}
        )

    def wrong_password_detected(self, user_email, ip, device):
        self.logger.warning(
            "Login attempt with wrong password", 
            extra={"user_email": self._mask_email(user_email), "ip": ip, "device": device}
        )

    def unknown_email_detected(self, user_email, ip, device):
        self.logger.warning(
            "Login attempt with unknown email", 
            extra={"user_email": self._mask_email(user_email), "ip": ip, "device": device}
        )

    def logout_success(self, user_id):
        self.logger.info(
            "User logged out successfully",
            extra={"user_id": user_id}
        )

    def changed_password(self, user_id, ip):
        self.logger.info(
            "User successfully changed password when first authorized",
            extra={"user_id": user_id, "ip": ip}
        )

    def password_reset_requested(self, user_id, ip):
        self.logger.warning(
            "Reset password token requested", extra={"user_id": user_id, "user_ip": ip}
        )

    def password_reset_success(self, user_id, ip):
        self.logger.info(
            "User successfully changed forgotten password",
            extra={"user_id": user_id, "ip": ip}
        )

    def token_reuse_detected(self, user_id, ip):
        self.logger.warning(
            "User's token has been reused", 
            extra={"user_id": user_id, "ip": ip}
        )
    
    def self_registration_attempt(self, user_email, ip):
        self.logger.warning(
            "User attempted to sign up",
            extra={"user_email": self._mask_email(user_email), "ip": ip}
        )

    def _mask_email(self, email):
        if not email or "@" not in email:
            return "***"
        
        name, domain = email.split("@")

        if len(name) <= 3:
            return f"{name[0]}***@{domain}"
        
        return f"{name[:3]}***@{domain}"



auth_audit = AuthAudit()
