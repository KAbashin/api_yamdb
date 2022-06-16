import csv

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Genre, Title, User

TABLES = {
    User: "users.csv",
    Category: "category.csv",
    Genre: "genre.csv",
    Title: "titles.csv",
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                f"{settings.BASE_DIR}/static/data/{csv_f}",
                "r",
                encoding="utf-8",
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(model(**data) for data in reader)
            print(f"  Importing data from file {csv_f}... OK")
        print()
        print("======================================")
        self.stdout.write(
            self.style.SUCCESS("The all data from .csv-files are imported.")
        )