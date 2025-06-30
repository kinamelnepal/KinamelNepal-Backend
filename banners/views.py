from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.mixins import MultiLookupMixin

from .filters import BannerFilter
from .models import Banner
from .serializers import BannerSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Banner"],
        summary="Retrieve a list of banners",
        description="Fetch all banners available in the system.",
        parameters=[
            OpenApiParameter(
                name="all",
                type=str,
                description="If set to `true`, disables pagination and returns all banners.",
                required=False,
                enum=["true", "false"],
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Banner"],
        summary="Retrieve a specific banner",
        description="Fetch detailed information about a specific banner by its ID.",
    ),
    create=extend_schema(
        tags=["Banner"],
        summary="Create a new banner",
        description="Create a new banner with the required details.",
    ),
    update=extend_schema(
        tags=["Banner"],
        summary="Update a banner's details",
        description="Modify an existing banner's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Banner"],
        summary="Partially update a banner's details",
        description="Modify some fields of an existing banner (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Banner"],
        summary="Delete a banner",
        description="Remove a banner from the system by its ID.",
    ),
)
class BannerViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]

    def paginate_queryset(self, queryset):
        """
        Override paginate_queryset to check for 'all=true' query parameter.
        """
        all_param = self.request.query_params.get("all", None)
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "subtitle"]
    ordering_fields = ["id", "display_order", "status", "start_date", "end_date"]
    filterset_class = BannerFilter
    ordering = ["display_order", "-start_date"]

    @extend_schema(
        tags=["Banner"],
        summary="Bulk Insert Banners",
        description="Insert multiple banners into the system in a single request.",
        request=BannerSerializer(many=True),
    )
    @action(detail=False, methods=["post"])
    def bulk_create(self, request, *args, **kwargs):
        """
        Bulk insert banners into the system.
        Accepts a list of banners to insert.
        """
        banners_data = request.data

        if not isinstance(banners_data, list) or len(banners_data) == 0:
            return Response(
                {"detail": "Expected 'banners' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BannerSerializer(data=banners_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(banners_data)} banners successfully inserted."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
