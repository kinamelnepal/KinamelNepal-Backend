from rest_framework import serializers
from .models import Address
from core.serializers import BaseModelSerializer

from users.models import User

class UserSlimAddressSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            'id','slug', 'first_name', 'last_name', 'email',
            'role', 'avatar','phone_number'
        ]
     

class AddressSerializer(BaseModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Address._meta.get_field('user').remote_field.model.objects.all(),
        source='user',
        write_only=True
    )
    user= UserSlimAddressSerializer(read_only=True)
    class Meta:
        model = Address
        fields = [
            'id', 'uuid','user', 'user_id', 'full_name', 'email', 'phone_number',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code',
            'country', 'address_type', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at']
