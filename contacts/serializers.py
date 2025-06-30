from core.serializers import BaseModelSerializer

from .models import Contact


class ContactSerializer(BaseModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "uuid",
            "full_name",
            "email",
            "phone",
            "message",
            "created_at",
            "updated_at",
        ]
