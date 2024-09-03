from django.core.management.base import BaseCommand
from hybrid.models import MagazineContent, MagazineInformation

class Command(BaseCommand):
    help = 'Clear Magazine Information and Content data'

    def handle(self, *args, **kwargs):
        MagazineInformation.objects.all().delete()
        MagazineContent.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared Magazine tables.'))
