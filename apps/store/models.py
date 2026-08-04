from django.conf import settings
from django.db import models

from apps.loyalty.models import TierRule

from .managers import OrderQuerySet, ProductQuerySet


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=0)

    # Trava o produto para torcedores que já atingiram (ao menos) este tier.
    # Ex: um produto só liberado para "Lenda B10".
    is_exclusive_tier = models.ForeignKey(
        TierRule, null=True, blank=True, on_delete=models.SET_NULL, related_name='exclusive_products',
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_available_for(self, profile) -> bool:
        if not self.is_exclusive_tier_id:
            return True
        current_rule = TierRule.objects.for_points(profile.total_points)
        current_order = current_rule.order if current_rule else 0
        return current_order >= self.is_exclusive_tier.order


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.code} (-{self.discount_percent}%)'

    def is_usable(self):
        if not self.active:
            return False
        if self.usage_limit is not None and self.times_used >= self.usage_limit:
            return False
        return True


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        PAID = 'PAID', 'Pago'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    total_original = models.DecimalField(max_digits=10, decimal_places=2)
    tier_discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=10, decimal_places=2)
    points_earned = models.IntegerField(default=0)
    free_shipping = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.pk} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
