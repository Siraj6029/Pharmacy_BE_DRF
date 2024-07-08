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
            "password": {"write_only": True, "required": True},
            "id": {"read_only": True},
            "username": {"required": True},
        }

    is_active = serializers.BooleanField(default=True)
    is_superuser = serializers.BooleanField(default=False)

    def create(self, validated_data: dict):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance: User, validated_data: dict):
        # if "username" in validated_data:
        #     raise ValidationError({"username": "username cannot be updated."})
        validated_data.pop("username", None)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_superuser = validated_data.get(
            "is_superuser", instance.is_superuser
        )
        password = validated_data.get("password", None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
