from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import User, Category, Genre, Title, Review

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import IsAdmin, AdminOrReadOnly, UserModeratorAdminOrReadOnly
from .serializers import (
    SignUpSerializer,
    CodeSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReadTitleSerializer,
    CommentSerializer,
    ReviewSerializer,
)


class SignUp(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            user = User.objects.create(
                username=username,
                email=email
            )
            token = default_token_generator.make_token(user)
            send_mail(
                subject='Приветствуем на API YAMDB!',
                message=f'Токен для авторизации: {token}',
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[email]
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.data.get('username')
        )
        confirmation_code = serializer.data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'Ваш токен доступа к API': str(token)},
                status=status.HTTP_200_OK
            )
        return Response(
            'Неверный токен доступа',
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.IsAuthenticated, IsAdmin,)
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=('GET', 'PATCH',),
        permission_classes=[permissions.IsAuthenticated],
        url_path='me',
    )
    def users_profile(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method != 'PATCH':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(
            user,
            context={'request': request},
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if self.request.user.role == (user.ADMIN
                                      or self.request.user.is_superuser):
            serializer.save()
        else:
            serializer.save(role=user.role)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleSerializer
        return ReadTitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (UserModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        user = self.request.user
        review = title.reviews.filter(author_id=user.id, title_id=title.id)
        if review.exists():
            raise ValidationError('Вы уже оставили Ваш отзыв!')
        serializer.save(author=user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (UserModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review = get_object_or_404(title.reviews,
                                   pk=self.kwargs.get('review_id'))
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'),
                                   title_id=self.kwargs.get('title_id'))
        user = self.request.user
        serializer.save(author=user, review=review)
