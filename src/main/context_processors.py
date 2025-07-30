from .models import Item


def cart(request):
    cart = request.session.get('cart', {})
    ids = [int(i) for i in cart.keys()]
    items = Item.objects.filter(id__in=ids)
    items_count = sum(cart.values())
    return {'cart': {'items': items, 'items_count': items_count, 'quantities': cart}}
