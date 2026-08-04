from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.loyalty.models import TierRule
from apps.store.models import Product

SAMPLE_PRODUCTS = [
    # --- Vestuário ---
    {
        'name': 'Camisa Oficial B10',
        'description': 'Camisa oficial da Bateria Dezorganizada, tecido dry-fit.',
        'price': 149.90,
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600',
        'stock': 80,
        'exclusive_code': None,
    },
    {
        'name': 'Camisa Reserva B10 Preta',
        'description': 'Segunda camisa da torcida, estampa discreta pro dia a dia.',
        'price': 149.90,
        'image_url': 'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=600',
        'stock': 60,
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
        'name': 'Balaclava B10 Stealth',
        'description': 'Bala clava preta com bordado B10, pro frio da arquibancada.',
        'price': 69.90,
        'image_url': 'https://images.unsplash.com/photo-1520975954732-35dd22299614?w=600',
        'stock': 40,
        'exclusive_code': None,
    },
    {
        'name': 'Pulseira Trançada B10 Ritmo',
        'description': 'Pulseira trançada com as cores da torcida.',
        'price': 24.90,
        'image_url': 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600',
        'stock': 150,
        'exclusive_code': None,
    },
    {
        'name': 'Pulseira de Silicone B10 Fogo',
        'description': 'Pulseira de silicone com o símbolo B10 em relevo.',
        'price': 14.90,
        'image_url': 'https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600',
        'stock': 200,
        'exclusive_code': None,
    },
    {
        'name': 'Pin Esmaltado B10 Caixa',
        'description': 'Pin esmaltado colecionável com a caixa de bateria da B10.',
        'price': 19.90,
        'image_url': 'https://images.unsplash.com/photo-1607969118442-b6c4a7f6a1b3?w=600',
        'stock': 120,
        'exclusive_code': None,
    },
    {
        'name': 'Pin Esmaltado B10 Fogo (Edição Especial)',
        'description': 'Pin esmaltado de edição limitada, símbolo B10 Fogo.',
        'price': 24.90,
        'image_url': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600',
        'stock': 50,
        'exclusive_code': None,
    },
    # --- Setup / periféricos gamer ---
    {
        'name': 'Mouse Gamer B10 Puxador',
        'description': 'Mouse gamer com sensor de precisão e acabamento B10.',
        'price': 199.90,
        'image_url': 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=600',
        'stock': 35,
        'exclusive_code': None,
    },
    {
        'name': 'Mouse Pad B10 Arquibancada (XL)',
        'description': 'Mouse pad extra grande com arte da arquibancada B10.',
        'price': 79.90,
        'image_url': 'https://images.unsplash.com/photo-1616588589676-62b3bd4ff6d2?w=600',
        'stock': 70,
        'exclusive_code': None,
    },
    {
        'name': 'Headset B10 Bateria Pro',
        'description': 'Headset gamer com microfone destacável, acabamento B10.',
        'price': 349.90,
        'image_url': 'https://images.unsplash.com/photo-1599669454699-248893623440?w=600',
        'stock': 25,
        'exclusive_code': 'PUXADOR',
    },
    {
        'name': 'Teclado Mecânico B10 Caos',
        'description': 'Teclado mecânico switch red com iluminação nas cores da B10.',
        'price': 449.90,
        'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600',
        'stock': 20,
        'exclusive_code': None,
    },
    # --- Itens de torcida / colecionáveis ---
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
