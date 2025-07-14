from core.serializers import BaseModelSerializer

from .models import ReturnPolicy


class ReturnPolicySerializer(BaseModelSerializer):
    class Meta:
        model = ReturnPolicy
        fields = ["id", "uuid", "title", "description", "created_at", "updated_at"]
