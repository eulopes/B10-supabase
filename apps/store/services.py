"""Casos de uso da loja: precificação de carrinho e checkout.

As views não calculam nada — só chamam esses services e renderizam o
resultado. Isso permite, por exemplo, reusar CartPricingService num futuro
endpoint de API ou numa integração de checkout externo (Shopify) sem
duplicar a regra de desconto/pontos.
"""
from dataclasses import dataclass, field
from decimal import Decimal

from django.db import transaction

from apps.loyalty.models import PointsTransaction, TierRule
from apps.loyalty.services import PointsEngineService

from .models import Order, OrderItem, Product

# Regra de negócio fixa do programa: a cada REAL_AMOUNT_PER_POINT reais
# gastos (sobre o total já com desconto do tier), 1 ponto é creditado.
REAL_AMOUNT_PER_POINT = Decimal('5')


@dataclass
class CartLine:
    product: Product
    quantity: int
    line_subtotal: Decimal


@dataclass
class CartSummary:
    lines: list = field(default_factory=list)
    subtotal: Decimal = Decimal('0')
    tier_discount_percent: int = 0
    tier_discount_value: Decimal = Decimal('0')
    free_shipping: bool = False
    total_final: Decimal = Decimal('0')
    points_to_earn: int = 0
    current_rule: TierRule = None
    next_rule: TierRule = None
    amount_to_next_tier: Decimal = Decimal('0')

    @property
    def is_empty(self):
        return not self.lines


class CartPricingService:
    """Recalcula o carrinho inteiro a partir da sessão a cada chamada —
    nunca confia em totais vindos do client."""

    def __init__(self, session_cart: dict, profile):
        self.session_cart = session_cart or {}
        self.profile = profile

    def build_summary(self) -> CartSummary:
        product_ids = [int(pid) for pid in self.session_cart.keys()]
        products = Product.objects.in_bulk(product_ids)

        lines = []
        subtotal = Decimal('0')
        for pid_str, quantity in self.session_cart.items():
            product = products.get(int(pid_str))
            if not product:
                continue
            line_subtotal = product.price * quantity
            subtotal += line_subtotal
            lines.append(CartLine(product=product, quantity=quantity, line_subtotal=line_subtotal))

        current_rule = TierRule.objects.for_points(self.profile.total_points) if self.profile else None
        next_rule = TierRule.objects.next_after(self.profile.total_points) if self.profile else None

        discount_percent = current_rule.discount_percent if current_rule else 0
        free_shipping = current_rule.free_shipping if current_rule else False
        discount_value = (subtotal * Decimal(discount_percent) / Decimal('100')).quantize(Decimal('0.01'))
        total_final = subtotal - discount_value
        points_to_earn = int(total_final / REAL_AMOUNT_PER_POINT)

        amount_to_next_tier = Decimal('0')
        if next_rule and self.profile:
            points_missing = max(0, next_rule.min_points - (self.profile.total_points + points_to_earn))
            amount_to_next_tier = Decimal(points_missing) * REAL_AMOUNT_PER_POINT

        return CartSummary(
            lines=lines,
            subtotal=subtotal,
            tier_discount_percent=discount_percent,
            tier_discount_value=discount_value,
            free_shipping=free_shipping,
            total_final=total_final,
            points_to_earn=points_to_earn,
            current_rule=current_rule,
            next_rule=next_rule,
            amount_to_next_tier=amount_to_next_tier,
        )


class EmptyCartError(Exception):
    pass


class CheckoutService:
    """Confirma um pedido: cria Order/OrderItem, baixa estoque e credita
    pontos através do PointsEngineService (nunca escreve pontos direto)."""

    @staticmethod
    @transaction.atomic
    def complete_purchase(user, profile, summary: CartSummary) -> Order:
        if summary.is_empty:
            raise EmptyCartError('Carrinho vazio.')

        order = Order.objects.create(
            user=user,
            total_original=summary.subtotal,
            tier_discount_applied=summary.tier_discount_value,
            total_final=summary.total_final,
            points_earned=summary.points_to_earn,
            free_shipping=summary.free_shipping,
            status=Order.Status.PAID,
        )
        for line in summary.lines:
            OrderItem.objects.create(
                order=order, product=line.product, quantity=line.quantity, unit_price=line.product.price,
            )
            Product.objects.filter(pk=line.product.pk).update(
                stock=max(0, line.product.stock - line.quantity)
            )

        if summary.points_to_earn > 0:
            PointsEngineService.award_points(
                user, summary.points_to_earn, reason=f'Compra #{order.id}', source=PointsTransaction.Source.PURCHASE,
            )

        return order
