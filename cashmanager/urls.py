from django.urls import path, include

from rest_framework.permissions import AllowAny

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Cash Manager API",
        default_version='v1',
        description="API endpoints for Cash Manager",
    ),
    public=True,
    permission_classes=[AllowAny],
)


urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('users/', include('apps.users.urls')),
    path('api/', include('apps.transaction.api.urls'))
]
