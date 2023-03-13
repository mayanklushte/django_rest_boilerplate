# -*- coding: utf-8 -*-

# Standard Library
from .utils import EmailUtilities
import logging

# Third Party Stuff
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

# Email Auth Stuff
logger = logging.getLogger(__name__)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailServiceSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get("email")
        session_token = attrs.get("session_token")

        backend = EmailUtilities()
        verification, token_validation = backend.validate_data(email=email, session_token=session_token)

        if verification is None:
            raise serializers.ValidationError(_("The link is not valid"))
        elif token_validation in [backend.SESSION_TOKEN_INVALID, backend.SESSION_TOKEN_EXPIRED, backend.SECURITY_CODE_EXPIRED]:
            raise serializers.ValidationError(_("The link has been expired or invalid"))

        return attrs


class EmailServiceWithOTPSerializer(EmailServiceSerializer):
    security_code = serializers.CharField(required=True)
