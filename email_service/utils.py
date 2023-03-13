import random
import jwt
from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from .models import EmailService
from .db_ops import store_email_tokens

DEFAULT_TOKEN_LENGTH = 6

class EmailUtilities:
    SECURITY_CODE_VALID = 0
    SECURITY_CODE_INVALID = 1
    SECURITY_CODE_EXPIRED = 2
    SECURITY_CODE_VERIFIED = 3
    SESSION_TOKEN_INVALID = 4
    SESSION_TOKEN_EXPIRED = 5

    @staticmethod
    def generate_security_code():
        token_length = django_settings.EMAIL_SERVICE.get(
            "TOKEN_LENGTH", DEFAULT_TOKEN_LENGTH
        )
        return get_random_string(token_length, allowed_chars="0123456789")

    @staticmethod
    def generate_session_token(email):
        data = {"email": email, "nonce": random.random()}
        session_token = jwt.encode(
            data, django_settings.SECRET_KEY, algorithm="HS256"
        )
        return session_token

    @staticmethod
    def check_security_code_expiry(stored_verification):
        time_difference = timezone.now() - stored_verification.created_at
        return time_difference.seconds > django_settings.EMAIL_SERVICE.get(
            "SECURITY_CODE_EXPIRATION_TIME"
        )

    def create_security_code_and_session_token(
        self, email, generate_security_code=True
    ):
        security_code = (
            self.generate_security_code() if generate_security_code else None
        )
        session_token = self.generate_session_token(email)
        store_email_tokens(email, security_code, session_token)
        return security_code, session_token

    def validate_data(self, email, session_token):
        stored_verification = EmailService.objects.filter(
            email=email, session_token=session_token
        ).first()

        if not stored_verification:
            return None, self.SESSION_TOKEN_INVALID

        if self.check_security_code_expiry(stored_verification):
            return stored_verification, self.SESSION_TOKEN_EXPIRED

        stored_verification.is_verified = True
        stored_verification.save()
        return stored_verification, self.SECURITY_CODE_VALID
