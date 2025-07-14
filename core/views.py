from django_countries import countries
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from geopy.geocoders import Nominatim
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


@extend_schema_view(
    list=extend_schema(
        summary="List API Keys",
        description="Retrieve a list of all API keys. Only accessible by superusers.",
        responses={200: APIKeySerializer(many=True)},
        tags=["API Keys"],
    ),
    retrieve=extend_schema(
        summary="Retrieve API Key",
        description="Get detailed information on a specific API key by its ID. Superuser access required.",
        responses={200: APIKeySerializer},
        tags=["API Keys"],
    ),
    create=extend_schema(
        summary="Create API Key",
        description=(
            "Creates a new API key. The key is auto‑generated and cannot be provided manually. "
            "Only accessible by superusers."
        ),
        responses={201: APIKeySerializer},
        tags=["API Keys"],
    ),
    update=extend_schema(
        summary="Update API Key",
        description="Update details of an API key (e.g. the active status). Superuser access required.",
        responses={200: APIKeySerializer},
        tags=["API Keys"],
    ),
    partial_update=extend_schema(
        summary="Partial Update API Key",
        description="Partially update an API key. Only accessible by superusers.",
        responses={200: APIKeySerializer},
        tags=["API Keys"],
    ),
    destroy=extend_schema(
        summary="Delete API Key",
        description="Delete an API key. Only accessible by superusers.",
        responses={204: OpenApiResponse(description="API key deleted successfully.")},
        tags=["API Keys"],
    ),
    deactivate=extend_schema(
        summary="Deactivate API Key",
        description="Deactivate an API key. This prevents the key from being used for API access.",
        responses={
            200: OpenApiResponse(description="API key deactivated successfully.")
        },
        tags=["API Keys"],
    ),
)
class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet restricted to superusers only for managing API keys.
    """

    queryset = APIKey.objects.all().order_by("-created_at")
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        """
        Create API Key (auto-generated).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def deactivate(self, request, pk=None):
        """
        Deactivate an API key.
        """
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({"status": "API key deactivated"}, status=status.HTTP_200_OK)
