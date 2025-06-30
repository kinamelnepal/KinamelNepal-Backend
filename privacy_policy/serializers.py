from core.serializers import BaseModelSerializer

from .models import PrivacyPolicy


class PrivacyPolicySerializer(BaseModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ["id", "uuid", "title", "description", "created_at", "updated_at"]
