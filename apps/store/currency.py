"""Conversão de moeda do carrinho (BRL -> USD/EUR).

Cotações fixas e atualizáveis manualmente aqui. Isoladas num módulo próprio
para, no futuro, trocar a fonte por uma API de câmbio em tempo real
(ex: exchangerate.host) sem tocar em CartPricingService — só a
implementação de `get_rates()` muda.
"""
from decimal import ROUND_HALF_UP, Decimal

# Quantos BRL equivalem a 1 unidade da moeda (cotação de referência).
BRL_PER_USD = Decimal('5.40')
BRL_PER_EUR = Decimal('6.30')

CURRENCIES = [
    {'code': 'BRL', 'symbol': 'R$', 'label': 'Real'},
    {'code': 'USD', 'symbol': 'US$', 'label': 'Dólar'},
    {'code': 'EUR', 'symbol': '€', 'label': 'Euro'},
]


def convert_from_brl(amount_brl: Decimal) -> dict:
    """Retorna {'BRL': Decimal, 'USD': Decimal, 'EUR': Decimal} a partir de um valor em reais."""
    cents = Decimal('0.01')
    return {
        'BRL': amount_brl.quantize(cents, rounding=ROUND_HALF_UP),
        'USD': (amount_brl / BRL_PER_USD).quantize(cents, rounding=ROUND_HALF_UP),
        'EUR': (amount_brl / BRL_PER_EUR).quantize(cents, rounding=ROUND_HALF_UP),
    }
