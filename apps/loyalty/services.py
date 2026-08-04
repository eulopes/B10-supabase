"""Casos de uso (services) do engine de fidelidade.

Este módulo é o único lugar autorizado a mudar UserProfile.total_points,
current_balance e tier. Qualquer ponto de entrada novo — checkout da loja,
check-in de evento, uma futura integração com Discord/Twitch/Shopify —
deve chamar PointsEngineService.award_points() em vez de tocar no model
diretamente. Isso mantém a regra de negócio num único lugar testável.
"""
from decimal import Decimal

from django.db import transaction

from apps.users.models import UserProfile

from .models import PointsTransaction, Redemption, RewardItem, TierRule
from .signals import points_awarded, tier_changed

# Conversão de pontos em desconto monetário: 1 ponto = R$ 0,10 (ex: 214 pts = R$ 21,40).
# Aplicada sobre current_balance (saldo gastável), não total_points (histórico, nunca decresce).
POINTS_TO_DISCOUNT_RATE = Decimal('0.10')


class InsufficientBalanceError(Exception):
    pass


class PointsEngineService:
    @staticmethod
    @transaction.atomic
    def award_points(user, amount, reason, source=PointsTransaction.Source.MANUAL):
        """Credita (ou debita, se amount < 0) pontos e recalcula o tier."""
        if amount == 0:
            return user.userprofile

        profile = UserProfile.objects.select_for_update().get(user=user)
        old_tier = profile.tier

        PointsTransaction.objects.create(user=user, amount=amount, reason=reason, source=source)

        profile.current_balance = max(0, profile.current_balance + amount)
        if amount > 0:
            profile.total_points += amount

        new_rule = TierRule.objects.for_points(profile.total_points)
        if new_rule:
            profile.tier = new_rule.code
        profile.save(update_fields=['total_points', 'current_balance', 'tier', 'updated_at'])

        points_awarded.send(
            sender=PointsEngineService, user=user, amount=amount,
            reason=reason, source=source, profile=profile,
        )
        if profile.tier != old_tier:
            tier_changed.send(sender=PointsEngineService, user=user, old_tier=old_tier, new_tier=profile.tier, profile=profile)

        return profile

    @staticmethod
    def reset(user, reason='Reset manual'):
        """Zera o saldo/histórico de um torcedor (uso administrativo)."""
        profile = UserProfile.objects.select_for_update().get(user=user)
        if profile.total_points:
            PointsTransaction.objects.create(
                user=user, amount=-profile.total_points, reason=reason, source=PointsTransaction.Source.MANUAL,
            )
        base_rule = TierRule.objects.ordered().first()
        profile.total_points = 0
        profile.current_balance = 0
        profile.tier = base_rule.code if base_rule else UserProfile.INICIANTE
        profile.save(update_fields=['total_points', 'current_balance', 'tier', 'updated_at'])
        return profile


class RedemptionService:
    @staticmethod
    @transaction.atomic
    def redeem(user, reward: RewardItem):
        profile = UserProfile.objects.select_for_update().get(user=user)
        if profile.current_balance < reward.cost_points:
            raise InsufficientBalanceError('Saldo de pontos insuficiente para este resgate.')
        if reward.stock <= 0:
            raise InsufficientBalanceError('Recompensa esgotada.')

        RewardItem.objects.filter(pk=reward.pk).update(stock=reward.stock - 1)
        PointsEngineService.award_points(
            user, -reward.cost_points, reason=f'Resgate: {reward.name}', source=PointsTransaction.Source.REDEMPTION,
        )
        return Redemption.objects.create(user=user, reward=reward, points_spent=reward.cost_points)


class DashboardService:
    """Agrega tudo que a tela de painel do torcedor precisa exibir."""

    @staticmethod
    def build_context(user):
        profile = user.userprofile
        current_rule = TierRule.objects.for_points(profile.total_points)
        next_rule = TierRule.objects.next_after(profile.total_points)

        if next_rule:
            span = next_rule.min_points - (current_rule.min_points if current_rule else 0)
            progressed = profile.total_points - (current_rule.min_points if current_rule else 0)
            progress_percent = max(0, min(100, round(progressed / span * 100))) if span else 100
            points_needed = max(0, next_rule.min_points - profile.total_points)
        else:
            progress_percent = 100
            points_needed = 0

        return {
            'profile': profile,
            'current_rule': current_rule,
            'next_rule': next_rule,
            'progress_percent': progress_percent,
            'points_needed': points_needed,
            'tier_rules': TierRule.objects.ordered(),
            'recent_transactions': PointsTransaction.objects.filter(user=user)[:15],
            'points_discount_value': profile.current_balance * POINTS_TO_DISCOUNT_RATE,
            'points_discount_rate': POINTS_TO_DISCOUNT_RATE,
        }
