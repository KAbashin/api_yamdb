from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentsViewSet, ReviewsViewSet, UserViewSet, send_confirmation_code, send_token

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename="users")
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', send_confirmation_code),
    path('v1/auth/signup/', send_token)
]
