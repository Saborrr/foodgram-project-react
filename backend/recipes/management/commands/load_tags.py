from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = "Загрузка тэгов"

    def handle(self, *args, **kwargs):
        data = [
            {"name": "завтрак", "color": "#48e22d", "slug": "breakfast"},
            {"name": "обед", "color": "#2da3e2", "slug": "dinner"},
            {"name": "ужин", "color": "#c72de2", "slug": "supper"},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(
            self.style.SUCCESS("***Тэги успешно загружены***")
        )
