from datetime import datetime
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.contrib.auth import authenticate, get_user_model
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    NotFound,
    ParseError,
)
from . import services
from rest_framework_simplejwt.views import TokenObtainPairView

from email_service.serializers import EmailServiceSerializer, EmailSerializer
from email_service.services import send_email_and_generate_token
from .serializers import (
    UserForgotPasswordSerializer,
    UserPasswordResetSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class UserProfileRegistrationView(generics.CreateAPIView):
    """
    To create a user based on POST request to 'user/register' endpoint.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()


class UserEmailVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query_params = {}
        query_params["email"] = self.request.data["email"]
        return User.objects.filter(**query_params).first()

    def get_serializer_class(self):
        return (
            EmailServiceSerializer
            if "session_token" in self.request.data.keys()
            else EmailSerializer
        )

    def post(self, request):
        user_db_details = self.get_queryset()
        if not user_db_details:
            raise NotFound({"error": "Account not found"})

        user_request_data = request.data
        serializer = self.get_serializer(data=user_request_data)

        if serializer.is_valid():
            if "session_token" not in user_request_data.keys():
                user_name = (
                    user_db_details.first_name.capitalize()
                    + " "
                    + user_db_details.last_name.capitalize()
                )
                send_email_and_generate_token(
                    user_db_details.email,
                    user_name=user_name,
                    email_template="../templates/mails/registration.html",
                    email_subject="Email Verification Link",
                )
                raise NotAuthenticated(
                    {"message": "Email is not verified. Verification mail has been sent"}
                )
            else:
                user_db_details.is_email_verified = True
                user_db_details.save(update_fields=["is_email_verified"])
                return Response(
                    {"message": "Email is verified successfully"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    """
    View that provides login functionalities via JWT Authentication.
    """

    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        user_request_data = self.request.data
        query_params = {}
        query_params["email"] = user_request_data["email"]
        return User.objects.filter(**query_params).first()

    def post(self, request, *args, **kwargs):
        user_db_details = self.get_queryset()
        if not user_db_details:
            raise NotFound({"message": "User does not exist"})

        user_request_data = self.request.data

        if not user_db_details.is_active:
            raise NotAuthenticated({"message": "User is not active"})

        user = authenticate(
            username=user_request_data["email"],
            password=user_request_data["password"],
        )

        if user is None:
            raise AuthenticationFailed(
                {"message": "Username and Password do not match"}
            )

        if not user_db_details.is_email_verified:
            user_name = (
                user_db_details.first_name.capitalize()
                + " "
                + user_db_details.last_name.capitalize()
            )
            send_email_and_generate_token(
                user_db_details.email,
                user_name=user_name,
                email_template="../templates/mails/registration.html",
                email_subject="Email Verification Link",
            )
            raise NotAuthenticated(
                {"message": "Email is not verified. Verification mail has been sent"}
            )
        else:
            response = services.get_tokens_for_user(user_db_details)
            user_db_details.last_login = datetime.now()
            user_db_details.save()
            response["message"] = "Login Successfully"
            return Response(response, status=status.HTTP_200_OK)


class UserForgotPasswordView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        user_request_data = self.request.data
        query_params = {}
        query_params["email"] = user_request_data["email"]
        return User.objects.filter(**query_params).first()

    def get_serializer_class(self):
        user_request_data = self.request.data
        if "security_code" not in user_request_data.keys():
            return UserForgotPasswordSerializer
        else:
            return UserPasswordResetSerializer

    def post(self, request):
        user_request_data = self.request.data
        user_db_details = self.get_queryset()
        serializer = self.get_serializer(data=user_request_data)
        serializer.is_valid(raise_exception=True)

        if not user_db_details.is_active:
            raise NotAuthenticated({"message": "User is not active"})

        if "security_code" not in user_request_data.keys():
            user_name = (
                user_db_details.first_name.capitalize()
                + " "
                + user_db_details.last_name.capitalize()
            )
            session_token = send_email_and_generate_token(
                serializer.data["email"],
                user_name=user_name,
                generate_security_code=True,
                email_template="../templates/mails/password_reset.html",
                email_subject="Password Reset Link",
            )
            return Response(
                {
                    "message": "The link has been sent to your Email",
                    "session_token": session_token,
                },
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            response = services.verify_otp_and_reset_password(
                user_request_data, user_db_details
            )
            return Response(response, status=status.HTTP_202_ACCEPTED)
