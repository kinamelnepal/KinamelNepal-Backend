from core.serializers import BaseModelSerializer

from .models import Faq


class FaqSerializer(BaseModelSerializer):
    class Meta:
        model = Faq
        fields = ["id", "uuid", "question", "answer", "created_at", "updated_at"]
