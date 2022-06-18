from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.generics import get_object_or_404
from rest_framework import filters, permissions, status, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import User, Category, Genre, Title, Review
from .mixins import CreateListDestroyViewSet
from .filters import TitleFilter
from .permissions import IsAdmin, AdminOrReadOnly
from .serializers import (
    SignUpSerializer,
    CodeSerializer,
    UserInfoSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReadTitleSerializer,
    CommentSerializer,
    ReviewSerializer,
)


class SignUp(APIView):
    permission_classes = (AllowAny,)

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
        if serializer.is_valid():
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = ['username']
    permission_classes = (IsAuthenticated, IsAdmin,)
#    lookup_field = 'username'
    queryset = User.objects.all()
#    ordering = ('username',)

    @action(detail=False,
            methods=('GET', 'PATCH',),
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserInfoSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data,
                            status=status.HTTP_200_OK
                            )

#Гриша
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
    filter_backends = (filters.SearchFilter,)
    filterset_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleSerializer
        return ReadTitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        queryset = title.reviews.all()
        return queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        user = self.request.user
        # review = Review.objects.filter(user_id=user.id, title_id=title.id)
        # if review.exists():
        #     raise ValidationError('Вы уже оставили Ваш отзыв!')
        serializer.save(author=user, title=title)

    def perform_update(self, serializer):
        super(ReviewsViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        super(ReviewsViewSet, self).perform_destroy(instance)


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review = get_object_or_404(title.reviews,
                                   pk=self.kwargs.get('review_id'))
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        user = self.request.user
        serializer.save(author=user, review=review)