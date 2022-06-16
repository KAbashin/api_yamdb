from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet, SignUp, GetToken

# app_name = "api"

router_v1 = SimpleRouter()

router_v1.register(r'users', UserViewSet)  # , basename="users"

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', GetToken.as_view()),
    path('v1/auth/signup/', SignUp.as_view()),
]
