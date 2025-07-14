from django_countries import countries
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from geopy.geocoders import Nominatim
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import BulkOperationsMixin, MultiLookupMixin
from core.utils import generate_bulk_schema_view, generate_crud_schema_view

from .models import APIKey
from .serializers import APIKeySerializer, GeoLocationSerializer


@extend_schema(
    responses={200: OpenApiResponse(description="List of countries")}, tags=["Core"]
)
class CountryListView(APIView):
    def get(self, request):
        country_choices = [(code, name) for code, name in countries]
        return Response(country_choices)


@extend_schema(
    tags=["Core"],
    parameters=[
        OpenApiParameter(
            name="address",
            description="The address to geocode",
            required=True,
            type=str,
            location=OpenApiParameter.QUERY,
        )
    ],
    responses={
        200: GeoLocationSerializer,
        400: OpenApiResponse(description="Bad request - Missing address parameter"),
        404: OpenApiResponse(description="Address not found"),
    },
)
class GeoLocationView(APIView):
    def get(self, request):
        address = request.GET.get("address", "")
        if not address:
            return Response({"error": "No address provided"}, status=400)

        geolocator = Nominatim(user_agent="my_django_app (contact@yourdomain.com)")

        location = geolocator.geocode(address)
        if location:
            return Response(
                {"latitude": location.latitude, "longitude": location.longitude}
            )

        return Response({"error": "Address not found"}, status=404)


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [AllowAny],
        "default": [IsAdminUser],
    }

    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        return [
            permission()
            for permission in self.permission_classes_by_action.get(
                self.action, self.permission_classes_by_action["default"]
            )
        ]

    def paginate_queryset(self, queryset):
        all_param = self.request.query_params.get("all")
        if all_param == "true":
            return None
        return super().paginate_queryset(queryset)


@generate_bulk_schema_view("API Key", APIKeySerializer)
@generate_crud_schema_view("API Key")
class APIKeyViewSet(MultiLookupMixin, BulkOperationsMixin, BaseViewSet):
    """
    ViewSet restricted to superusers only for managing API keys.
    """

    queryset = APIKey.objects.all().order_by("-created_at")
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    bulk_schema_tag = "API Key"

    def create(self, request, *args, **kwargs):
        """
        Create API Key (auto-generated).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["API Key"],
        summary="Deactivate API Key",
        description="Deactivate a specific API key by setting its `is_active` field to `False`.",
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def deactivate(self, request, pk=None):
        """
        Deactivate an API key.
        """
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({"status": "API key deactivated"}, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """
    A simple health-check endpoint to verify the API's availability.
    """

    @extend_schema(
        summary="Health Check API",
        tags=["Test"],
        description="Returns the health status of the API.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "message": {
                        "type": "string",
                        "example": "The API is running smoothly.",
                    },
                },
            }
        },
    )
    def get(self, request):
        return Response(
            {"status": "healthy", "message": "The API is running smoothly."},
            status=status.HTTP_200_OK,
        )
