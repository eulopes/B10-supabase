from django.contrib.auth.models import User
from django.db import models


class UserProfileQuerySet(models.QuerySet):
    """Abstrai consultas de negócio sobre torcedores, mantendo a regra fora das views."""

    def for_tier(self, tier_code):
        return self.filter(tier=tier_code)

    def with_points_at_least(self, points):
        return self.filter(total_points__gte=points)

    def top_by_points(self, limit=10):
        return self.order_by('-total_points')[:limit]


class UserProfile(models.Model):
    """Perfil de fidelidade do torcedor. É o 'estado atual' — o histórico
    auditável de cada crédito/débito de pontos vive em apps.loyalty.PointsTransaction.
    O campo `tier` é um cache denormalizado, recalculado pelo PointsEngineService
    (apps.loyalty.services) a cada mudança de saldo — nunca deve ser editado à mão
    sem passar pelo engine, sob risco de dessincronizar do saldo real.
    """

    # Códigos de tier. A régua de pontos/desconto de cada um vive em
    # apps.loyalty.models.TierRule (dado configurável, não hardcoded aqui).
    INICIANTE = 'INICIANTE'
    RITMISTA = 'RITMISTA'
    PUXADOR = 'PUXADOR'
    LENDA = 'LENDA'

    TIER_CHOICES = [
        (INICIANTE, 'B10 Iniciante'),
        (RITMISTA, 'Ritmista'),
        (PUXADOR, 'Puxador do Caos'),
        (LENDA, 'Lenda B10'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar_url = models.URLField(blank=True)

    total_points = models.IntegerField(default=0, help_text='Acumulado histórico, nunca decresce.')
    current_balance = models.IntegerField(default=0, help_text='Saldo disponível para resgates/trocas.')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default=INICIANTE)

    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileQuerySet.as_manager()

    class Meta:
        verbose_name = 'Perfil do Torcedor'
        verbose_name_plural = 'Perfis dos Torcedores'

    def __str__(self):
        return f'{self.user.username} ({self.get_tier_display()})'
