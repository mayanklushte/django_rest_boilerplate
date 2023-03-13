from rest_framework_simplejwt.tokens import RefreshToken
from email_service.serializers import EmailServiceWithOTPSerializer

REFRESH_TOKEN = "refresh"
ACCESS_TOKEN = "access"

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        REFRESH_TOKEN: str(refresh),
        ACCESS_TOKEN: str(refresh.access_token),
    }


def verify_otp(user_request_data):
    serializer = EmailServiceWithOTPSerializer(data=user_request_data)
    serializer.is_valid(raise_exception=True)
    return True


def reset_password(user_db_details, new_password):
    user_db_details.is_email_verified = True
    user_db_details.set_password(new_password)
    user_db_details.save()
    return True


def verify_otp_and_reset_password(user_request_data, user_db_details):
    if verify_otp(user_request_data) and reset_password(user_db_details, user_request_data["password"]):
        return {
            "message": "Password Reset Successfully"
        }
