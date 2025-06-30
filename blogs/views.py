from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.mixins import MultiLookupMixin

from .filters import BlogFilter
from .models import Blog, BlogCategory
from .serializers import BlogCategorySerializer, BlogSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Blog"],
        summary="Retrieve a list of blogs",
        description="Fetch all blogs available in the system.",
    ),
    retrieve=extend_schema(
        tags=["Blog"],
        summary="Retrieve a specific blog",
        description="Fetch detailed information about a specific blog by its ID.",
    ),
    create=extend_schema(
        tags=["Blog"],
        summary="Create a new blog",
        description="Create a new blog with the required details.",
    ),
    update=extend_schema(
        tags=["Blog"],
        summary="Update a blog's details",
        description="Modify an existing blog's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["Blog"],
        summary="Partially update a blog's details",
        description="Modify some fields of an existing blog (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["Blog"],
        summary="Delete a blog",
        description="Remove a blog from the system by its ID.",
    ),
)
class BlogViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "category__name"]
    filterset_class = BlogFilter
    ordering_fields = ["id", "date", "created_at", "updated_at"]
    ordering = ["-created_at"]

    @extend_schema(
        tags=["Blog"],
        summary="Bulk Insert Blogs",
        description="Insert multiple blogs into the system in a single request.",
        request=BlogSerializer(many=True),
    )
    @action(detail=False, methods=["post"])
    def bulk_insert(self, request, *args, **kwargs):
        """
        Bulk insert blogs into the system.
        Accepts a list of blogs to insert.
        """
        blogs_data = request.data

        if not isinstance(blogs_data, list) or len(blogs_data) == 0:
            return Response(
                {"detail": "Expected 'blogs' to be a non-empty list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BlogSerializer(data=blogs_data, many=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": f"{len(blogs_data)} blogs successfully inserted."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        tags=["BlogCategory"],
        summary="Retrieve a list of blog categories",
        description="Fetch all blog categories available in the system.",
    ),
    retrieve=extend_schema(
        tags=["BlogCategory"],
        summary="Retrieve a specific blog category",
        description="Fetch detailed information about a specific blog category by its ID.",
    ),
    create=extend_schema(
        tags=["BlogCategory"],
        summary="Create a new blog category",
        description="Create a new blog category with the required details.",
    ),
    update=extend_schema(
        tags=["BlogCategory"],
        summary="Update a blog category's details",
        description="Modify an existing blog category's information entirely (PUT method).",
    ),
    partial_update=extend_schema(
        tags=["BlogCategory"],
        summary="Partially update a blog category's details",
        description="Modify some fields of an existing blog category (PATCH method).",
    ),
    destroy=extend_schema(
        tags=["BlogCategory"],
        summary="Delete a blog category",
        description="Remove a blog category from the system by its ID.",
    ),
)
class BlogCategoryViewSet(MultiLookupMixin, viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return [AllowAny()]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
