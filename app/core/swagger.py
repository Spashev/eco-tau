from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from django.urls import path

from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="SuperAPP API",
      default_version='v1',
      description="Description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="s.nurken92@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


swagger_patterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
