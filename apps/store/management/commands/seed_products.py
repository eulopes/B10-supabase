from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.loyalty.models import TierRule
from apps.store.models import Product

SAMPLE_PRODUCTS = [
    {
        'name': 'Camisa Oficial B10',
        'description': 'Camisa oficial da Bateria Dezorganizada, tecido dry-fit.',
        'price': 149.90,
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600',
        'stock': 80,
        'exclusive_code': None,
    },
    {
        'name': 'Boné B10 Fogo',
        'description': 'Boné bordado com o símbolo da bateria.',
        'price': 89.90,
        'image_url': 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=600',
        'stock': 60,
        'exclusive_code': None,
    },
    {
        'name': 'Bandeira de Arquibancada B10',
        'description': 'Bandeira grande pra levantar a torcida no setor.',
        'price': 199.90,
        'image_url': 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=600',
        'stock': 25,
        'exclusive_code': None,
    },
    {
        'name': 'Caixa de Som Portátil B10',
        'description': 'Pra não deixar o grito da torcida sem batida.',
        'price': 349.00,
        'image_url': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600',
        'stock': 15,
        'exclusive_code': None,
    },
    {
        'name': 'Instrumento de Bateria (Caixa) Mini',
        'description': 'Réplica de caixa de bateria, item colecionável.',
        'price': 259.00,
        'image_url': 'https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?w=600',
        'stock': 10,
        'exclusive_code': None,
    },
    {
        'name': 'Jaqueta Lenda B10 (Edição Limitada)',
        'description': 'Jaqueta exclusiva para torcedores nível Lenda B10.',
        'price': 599.00,
        'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600',
        'stock': 8,
        'exclusive_code': 'LENDA',
    },
]


class Command(BaseCommand):
    help = 'Popula o catálogo com produtos de exemplo da B10.'

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_PRODUCTS:
            slug = slugify(data['name'])
            exclusive_tier = None
            if data['exclusive_code']:
                exclusive_tier = TierRule.objects.filter(code=data['exclusive_code']).first()

            _, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'price': data['price'],
                    'image_url': data['image_url'],
                    'stock': data['stock'],
                    'is_exclusive_tier': exclusive_tier,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'{created_count} produtos criados, {len(SAMPLE_PRODUCTS) - created_count} atualizados.'
        ))
