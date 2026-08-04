from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from apps.loyalty.models import TierRule

from .currency import convert_from_brl
from .models import Order, Product
from .services import CartPricingService, CheckoutService, EmptyCartError


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def catalog(request):
    products = Product.objects.select_related('is_exclusive_tier').all()
    profile = request.user.userprofile if request.user.is_authenticated else None

    products_with_availability = [
        {'product': p, 'available': p.is_available_for(profile) if profile else not p.is_exclusive_tier_id}
        for p in products
    ]
    return render(request, 'store/catalog.html', {'products_with_availability': products_with_availability})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    profile = request.user.userprofile

    if not product.is_available_for(profile):
        messages.error(request, f'"{product.name}" é exclusivo para torcedores {product.is_exclusive_tier.label}.')
        return redirect('catalog')

    cart = _get_cart(request)
    key = str(product.id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    messages.success(request, f'"{product.name}" adicionado ao carrinho.')

    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(referer)
    return redirect('catalog')


@login_required
def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect('cart_detail')


@login_required
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        cart = _get_cart(request)
        key = str(product_id)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        if quantity <= 0:
            cart.pop(key, None)
        else:
            cart[key] = quantity
        _save_cart(request, cart)
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    summary = CartPricingService(_get_cart(request), request.user.userprofile).build_summary()
    return render(request, 'store/cart.html', {'summary': summary})


@login_required
def checkout(request):
    if request.method != 'POST':
        return redirect('cart_detail')

    profile = request.user.userprofile
    summary = CartPricingService(_get_cart(request), profile).build_summary()

    if summary.is_empty:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart_detail')

    return redirect('payment_gateway')


@login_required
def payment_gateway(request):
    profile = request.user.userprofile
    summary = CartPricingService(_get_cart(request), profile).build_summary()

    if summary.is_empty:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart_detail')

    if request.method == 'POST':
        card_number = request.POST.get('card_number', '').replace(' ', '')
        card_name = request.POST.get('card_name', '').strip()
        card_cvv = request.POST.get('card_cvv', '').strip()

        errors = []
        if len(card_number) < 13 or not card_number.isdigit():
            errors.append('Número de cartão inválido.')
        if not card_name:
            errors.append('Informe o nome impresso no cartão.')
        if len(card_cvv) < 3 or not card_cvv.isdigit():
            errors.append('CVV inválido.')
        if not errors and card_number.startswith('4000'):
            errors.append('Pagamento recusado pela operadora do cartão. Tente outro cartão.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'store/payment_gateway.html', {'summary': summary, 'card_name': card_name})

        try:
            order = CheckoutService.complete_purchase(request.user, profile, summary)
        except EmptyCartError:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('cart_detail')

        _save_cart(request, {})
        messages.success(request, 'Pagamento aprovado!')
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'store/payment_gateway.html', {'summary': summary})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    context = {'order': order, 'total_by_currency': convert_from_brl(order.total_final)}
    return render(request, 'store/order_confirmation.html', context)
