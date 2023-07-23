from django.urls import path, include


urlpatterns = [
    path('users/', include('apps.users.urls')),
    path('api/', include('apps.transaction.api.urls')),
]
