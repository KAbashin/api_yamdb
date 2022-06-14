from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .permissions import IsAdmin
from .serializers import (
    ConfirmationCodeSerializer,
    EmailSerializer,
    UserMeSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_confirmation_code(request):
    if request.method == "POST":
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        if username == 'me':
            return Response(
                'Этот никнейм зарезервирован, используйте другой никнейм',
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                "Пользователь с таким e-mail уже зарегистрирован.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif User.objects.filter(username=username).exists():
            return Response(
                "Пользователь с таким username уже зарегистрирован.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user = User.objects.create(email=email, username=username)
            token = default_token_generator.make_token(user)
            resp = {'email': email, 'username': username}
            send_mail(
                subject='Код подтверждения',
                message=str(token),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    email,
                ],
            )
            return Response(
                resp,
                status=status.HTTP_200_OK,
            )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_token(request):
    serialezer = ConfirmationCodeSerializer(data=request.data)
    serialezer.is_valid(raise_exception=True)
    confirmation_code = serialezer.validated_data.get('confirmation_code')
    username = serialezer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    if not confirmation_code:
        return Response(
            'В запросе отсутствует сonfirmation_code',
            status=status.HTTP_400_BAD_REQUEST
        )
    if not username:
        return Response(
            'В запросе отсутствует username',
            status=status.HTTP_400_BAD_REQUEST
        )
    token_check = default_token_generator.check_token(user, confirmation_code)
    if token_check:
        refresh = RefreshToken.for_user(user)
        return Response(
            f'Токен обновлен. Новый токен: {refresh.access_token}',
            status=status.HTTP_200_OK
        )
    return Response(
        'Неверный confirmation_code.',
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    queryset = User.objects.all()
    search_fields = ('username',)
    ordering = ('username',)

    @action(detail=False,
            methods=('get', 'patch',),
            serializer_class=UserMeSerializer,
            permission_classes=[permissions.IsAuthenticated]
            )
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data,
                                             partial=True
                                             )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
