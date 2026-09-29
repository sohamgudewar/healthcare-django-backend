"""
URL Configuration for Healthcare Backend.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


class APIRootView(APIView):
    """Healthcare Backend API Root / Health Check."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiTypes.OBJECT},
        tags=['Health & Discovery'],
        summary='API Service Health Check and Root Sitemap',
    )
    def get(self, request):
        return Response(
            {
                'status': 'healthy',
                'service': 'Healthcare Management Backend API',
                'version': '1.0.0',
                'endpoints': {
                    'authentication': {
                        'register': '/api/auth/register/',
                        'login': '/api/auth/login/',
                        'token_refresh': '/api/auth/token/refresh/',
                        'profile': '/api/auth/me/',
                    },
                    'patients': '/api/patients/',
                    'doctors': '/api/doctors/',
                    'mappings': '/api/mappings/',
                    'documentation': {
                        'swagger': '/api/docs/',
                        'redoc': '/api/redoc/',
                        'openapi_schema': '/api/schema/',
                    },
                },
            }
        )


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Root / Health check
    path('', APIRootView.as_view(), name='api-root'),
    path('api/', APIRootView.as_view(), name='api-index'),

    # Domain APIs
    path('api/auth/', include('apps.authentication.urls', namespace='auth')),
    path('api/patients/', include('apps.patients.urls', namespace='patients')),
    path('api/doctors/', include('apps.doctors.urls', namespace='doctors')),
    path('api/mappings/', include('apps.mappings.urls', namespace='mappings')),

    # OpenAPI 3.0 / Swagger Interactive Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
