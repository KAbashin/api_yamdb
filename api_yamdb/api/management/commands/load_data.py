import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Title, Genre, Review, Comment, User


class Command(BaseCommand):

    def handle(self, *args, **options):

        file_path = os.path.join(settings.BASE_DIR, 'static/data',
                                 'category.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Category.objects.get_or_create(
                    name=row[1],
                    slug=row[2],
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data', 'genre.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Genre.objects.get_or_create(
                    name=row[1],
                    slug=row[2]
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data',
                                 'titles.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Title.objects.get_or_create(
                    name=row[1],
                    year=row[2],
                    category=Category.objects.get(id=row[3])
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data', 'users.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = User.objects.get_or_create(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6],
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data',
                                 'review.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Review.objects.get_or_create(
                    title=Title.objects.get(id=row[1]),
                    text=row[2],
                    author=User.objects.get(id=row[3]),
                    score=int(row[4]),
                    pub_date=row[5],
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data',
                                 'comments.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                _, created = Comment.objects.get_or_create(
                    review=Review.objects.get(id=row[1]),
                    text=row[2],
                    author=User.objects.get(id=int(row[3])),
                    pub_date=row[4],
                )
            f.close()

        file_path = os.path.join(settings.BASE_DIR, 'static/data',
                                 'genre_title.csv')

        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            first_line = 1
            for row in reader:
                if first_line:
                    first_line = 0
                    continue
                Title.objects.get(id=row[1]).genre.add(
                    Genre.objects.get(id=row[2])
                )
            f.close()
