from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from core.serializers import BaseModelSerializer
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



