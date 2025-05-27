from .models import PrivacyPolicy
from core.serializers import BaseModelSerializer


class PrivacyPolicySerializer(BaseModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            'id', 'uuid', 'title', 'description',
            'created_at', 'updated_at'
        ]
