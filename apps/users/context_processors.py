def loyalty_context(request):
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'userprofile', None)
    cart = request.session.get('cart', {})

    return {
        'nav_profile': profile,
        'cart_items_count': sum(cart.values()) if cart else 0,
    }
