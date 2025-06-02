from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from core.serializers import BaseModelSerializer
from django.core.exceptions import ValidationError

class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'uuid', 'slug', 'first_name', 'last_name', 'email', 'password', "is_superuser", "is_staff",
            'role', 'avatar','address', 'country', 'state', 'city', 'post_code', 'phone_number',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            try:
                validate_password(password)
            except Exception as e:
                raise serializers.ValidationError({'password': list(e.messages)})
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            try:
                validate_password(password)
            except Exception as e:
                raise serializers.ValidationError({'password': list(e.messages)})
            instance.set_password(password)
        instance.save()
        return instance

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'email', 'avatar', 'password', 'address', 'country', 'state', 'city', 'post_code', 'phone_number']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})
        return value

    def validate_new_password(self, value):
        validate_password(value)  
        return value





class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        print(value, 'value in validate email')
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        try:
            validate_password(data["new_password"])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        return data
    

class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()
