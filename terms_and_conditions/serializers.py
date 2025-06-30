from core.serializers import BaseModelSerializer

from .models import TermsAndConditions


class TermsAndConditionsSerializer(BaseModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ["id", "uuid", "title", "description", "created_at", "updated_at"]
