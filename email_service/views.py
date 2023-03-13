# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .base import response
from .serializers import (
    EmailSerializer,
    EmailServiceSerializer,
    EmailServiceWithOTPSerializer,
)
from .services import send_email_and_generate_token


class EmailServiceViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def _send_email_and_generate_token(self, email, generate_security_code=False):
        return send_email_and_generate_token(str(email), generate_security_code=generate_security_code)

    @action(detail=False, methods=["POST"], serializer_class=EmailSerializer)
    def send(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = self._send_email_and_generate_token(
            serializer.validated_data["email"], generate_security_code=True
        )
        return response.Ok({"session_token": session_token})

    @action(detail=False, methods=["POST"], serializer_class=EmailSerializer)
    def send_token(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = self._send_email_and_generate_token(serializer.validated_data["email"])
        return response.Ok({"session_token": session_token})

    @action(detail=False, methods=["POST"], serializer_class=EmailServiceWithOTPSerializer)
    def verify(self, request):
        self.get_serializer(data=request.data).is_valid(raise_exception=True)
        return response.Ok({"message": "Security code is valid."})

    @action(detail=False, methods=["POST"], serializer_class=EmailServiceSerializer)
    def verify_token(self, request):
        self.get_serializer(data=request.data).is_valid(raise_exception=True)
        return response.Ok({"message": "Security code is valid."})
