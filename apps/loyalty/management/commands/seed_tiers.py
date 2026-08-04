from django.core.management.base import BaseCommand

from apps.loyalty.models import TierRule
from apps.users.models import UserProfile

TIERS = [
    {
        'code': UserProfile.INICIANTE, 'label': 'B10 Iniciante',
        'min_points': 0, 'max_points': 499, 'discount_percent': 0, 'free_shipping': False, 'order': 0,
    },
    {
        'code': UserProfile.RITMISTA, 'label': 'Ritmista',
        'min_points': 500, 'max_points': 1499, 'discount_percent': 5, 'free_shipping': False, 'order': 1,
    },
    {
        'code': UserProfile.PUXADOR, 'label': 'Puxador do Caos',
        'min_points': 1500, 'max_points': 3499, 'discount_percent': 10, 'free_shipping': False, 'order': 2,
    },
    {
        'code': UserProfile.LENDA, 'label': 'Lenda B10',
        'min_points': 3500, 'max_points': None, 'discount_percent': 15, 'free_shipping': True, 'order': 3,
    },
]


class Command(BaseCommand):
    help = 'Popula a régua de tiers de fidelidade B10.'

    def handle(self, *args, **options):
        for data in TIERS:
            TierRule.objects.update_or_create(code=data['code'], defaults=data)
        self.stdout.write(self.style.SUCCESS(f'{len(TIERS)} tiers configurados.'))
