from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CommentsViewSet,
                    ReviewsViewSet,
                    UserViewSet,
                    SignUp,
                    GetToken,
                    CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet
                    )

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename="users")
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments')
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', GetToken.as_view()),
    path('v1/auth/signup/', SignUp.as_view())
]
