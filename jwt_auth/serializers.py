from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(object):
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "phone_number",
            "date_of_birth",
            "location",
            "interests",
            "bio",
            "banner_image"
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, attrs):
        password = attrs.get("password")
        user = User(**attrs)
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e})
        return attrs


class UserForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        email = attrs.get("email", None)
        if not email:
            raise serializers.ValidationError("Email field does not exist")

        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("No user found for given email")

        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def _get_user(self):
        request_data = self.context["request"].data
        email = request_data.get("email")
        return get_object_or_404(User, email=email)

    def validate_password(self, password):
        user = self._get_user()
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e})
        return password
