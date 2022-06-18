from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import User, Category, Genre, Title, Review, Comment


class CodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'confirmation_code'
        ]


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        ]

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                f'Регистрация с именем пользователя {value} запрещена!'
            )
        return value


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                f'Регистрация с именем пользователя {value} запрещена!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        author = self.context['request'].user.id
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(title=title, author=author).exists():
            raise ValidationError(
                'Вы уже оставили Ваш отзыв!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')


class ReadTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
