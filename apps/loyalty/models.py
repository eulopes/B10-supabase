from django.conf import settings
from django.db import models


class TierRuleQuerySet(models.QuerySet):
    """Abstrai a régua de tiers do banco: quem quiser saber 'que tier vale
    para X pontos' ou 'qual o próximo tier' passa por aqui, nunca por
    if/elif espalhados pelo código. Adicionar um tier novo (ou mudar o
    desconto de um existente) é só um registro novo/editado nesta tabela.
    """

    def ordered(self):
        return self.order_by('order')

    def for_points(self, points):
        return (
            self.filter(min_points__lte=points)
            .filter(models.Q(max_points__isnull=True) | models.Q(max_points__gte=points))
            .order_by('-min_points')
            .first()
        )

    def next_after(self, points):
        return self.filter(min_points__gt=points).order_by('min_points').first()


class TierRule(models.Model):
    """Configuração de um nível de fidelidade (dado, não código)."""

    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)
    min_points = models.PositiveIntegerField()
    max_points = models.PositiveIntegerField(null=True, blank=True, help_text='Vazio = sem teto (tier máximo).')
    discount_percent = models.PositiveSmallIntegerField(default=0)
    free_shipping = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, help_text='Ordem de exibição/progressão (0 = mais baixo).')

    objects = TierRuleQuerySet.as_manager()

    class Meta:
        ordering = ['order']
        verbose_name = 'Regra de Tier'
        verbose_name_plural = 'Régua de Tiers'

    def __str__(self):
        return f'{self.label} ({self.discount_percent}% OFF)'


class PointsTransaction(models.Model):
    """Extrato auditável: toda concessão/dedução de pontos vira uma linha
    aqui, sempre através do PointsEngineService — nunca editando
    UserProfile.total_points diretamente. `source` existe para já suportar
    futuras origens externas (Discord, Twitch, Shopify) sem migração.
    """

    class Source(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Compra na loja'
        EVENT_CHECKIN = 'EVENT_CHECKIN', 'Check-in em evento'
        REDEMPTION = 'REDEMPTION', 'Resgate de recompensa'
        MANUAL = 'MANUAL', 'Ajuste manual'
        EXTERNAL_DISCORD = 'EXTERNAL_DISCORD', 'Discord'
        EXTERNAL_TWITCH = 'EXTERNAL_TWITCH', 'Twitch'
        EXTERNAL_SHOPIFY = 'EXTERNAL_SHOPIFY', 'Shopify'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_transactions')
    amount = models.IntegerField(help_text='Positivo = crédito, negativo = débito (ex: resgate).')
    reason = models.CharField(max_length=200)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transação de Pontos'
        verbose_name_plural = 'Extrato de Pontos'

    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f'{self.user.username}: {sign}{self.amount} pts ({self.reason})'


class RewardItem(models.Model):
    """Item resgatável na loja de recompensas (troca de pontos)."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    cost_points = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'

    def __str__(self):
        return f'{self.name} ({self.cost_points} pts)'


class Redemption(models.Model):
    """Registro de um resgate de recompensa por um torcedor."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(RewardItem, on_delete=models.PROTECT, related_name='redemptions')
    points_spent = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resgate'
        verbose_name_plural = 'Resgates'

    def __str__(self):
        return f'{self.user.username} resgatou {self.reward.name}'
