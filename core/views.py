from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse,OpenApiExample
from django_countries import countries
from rest_framework.views import APIView
from rest_framework.response import Response
from geopy.geocoders import Nominatim
from .serializers import GeoLocationSerializer

@extend_schema(
    responses={200: OpenApiResponse(description='List of countries')},
    tags=["Core"]
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
        404: OpenApiResponse(description="Address not found")
    },
)
class GeoLocationView(APIView):
    def get(self, request):
        address = request.GET.get('address', '')
        if not address:
            return Response({"error": "No address provided"}, status=400)

        geolocator = Nominatim(user_agent="my_django_app (contact@yourdomain.com)")

        location = geolocator.geocode(address)
        if location:
            return Response({
                "latitude": location.latitude,
                "longitude": location.longitude
            })
        
        return Response({"error": "Address not found"}, status=404)



