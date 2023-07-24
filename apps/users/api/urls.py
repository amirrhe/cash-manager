from django.urls import path
from apps.users.api.views import RegisterUserView, LoginView

urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name="login")
]
