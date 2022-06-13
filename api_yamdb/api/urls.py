from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router_v1 = DefaultRouter()

router_v1.register('users', views.UserViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls))
]