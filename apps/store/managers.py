from django.db import models


class ProductQuerySet(models.QuerySet):
    """Abstrai regras de catálogo (ex: exclusividade por tier) do ORM cru."""

    def in_stock(self):
        return self.filter(stock__gt=0)

    def available_for_tier(self, tier_order):
        """Produtos sem trava de tier, ou cujo tier mínimo o torcedor já atingiu."""
        return self.filter(
            models.Q(is_exclusive_tier__isnull=True) | models.Q(is_exclusive_tier__order__lte=tier_order)
        )

    def exclusive(self):
        return self.filter(is_exclusive_tier__isnull=False)


class OrderQuerySet(models.QuerySet):
    def paid(self):
        return self.filter(status='PAID')

    def for_user(self, user):
        return self.filter(user=user)
