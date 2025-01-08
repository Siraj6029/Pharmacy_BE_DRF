# users/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_superuser",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "id": {"read_only": True},
            "username": {"required": True},
        }

    is_active = serializers.BooleanField(default=True)
    is_superuser = serializers.BooleanField(default=False)

    def create(self, validated_data: dict):
        if not validated_data.get("password"):
            raise ValidationError("Password field is required.")
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("username", None)

        # Update other user fields
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_superuser = validated_data.get(
            "is_superuser", instance.is_superuser
        )

        if password:
            instance.set_password(password)  # If password is provided, update it

        instance.save()
        return instance
