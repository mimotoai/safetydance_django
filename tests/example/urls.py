from django.urls import include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from . import rest

router = DefaultRouter()
router.register(r"simple", rest.SimpleViewSet)
router.register(r"users", rest.UserViewSet)
schema_view = get_schema_view("Test safetydance_django API")

urlpatterns = [
    re_path(r"^api/", include(router.urls), name="api"),
    re_path(r"^api/schema", schema_view, name="api-schema"),
    re_path(
        r"^api/rest-framework/auth",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
]
