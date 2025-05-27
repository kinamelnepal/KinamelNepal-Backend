from .models import ReturnPolicy
from core.serializers import BaseModelSerializer


class ReturnPolicySerializer(BaseModelSerializer):
    class Meta:
        model = ReturnPolicy
        fields = [
            'id', 'uuid', 'title', 'description',
            'created_at', 'updated_at'
        ]
