from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, send_confirmation_code, send_token

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename="users")

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', send_confirmation_code),
    path('v1/auth/signup/', send_token)
]
