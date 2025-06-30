from core.serializers import BaseModelSerializer

from .models import Banner


class BannerSerializer(BaseModelSerializer):
    class Meta:
        model = Banner
        fields = [
            "id",
            "uuid",
            "title",
            "subtitle",
            "image",
            "call_to_action_link",
            "call_to_action_text",
            "show_call_to_action",
            "description",
            "status",
            "display_order",
            "start_date",
            "end_date",
            "display_location",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
