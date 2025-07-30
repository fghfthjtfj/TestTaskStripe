import os
import stripe
from ..models import *


def write_order_data(cart):
    order = Order.objects.create()

    order_items = []
    for item_id, qty in cart.items():
        item = Item.objects.get(pk=item_id)
        order_item = OrderItem.objects.create(order=order, item=item, quantity=qty)
        order_items.append(order_item)

    currency = order_items[0].item.currency
    tax = Tax.objects.filter(currency=currency).first()
    discount = Discount.objects.filter(currency=currency).first()

    tax_id = tax.stripe_id if tax else None
    discount_id = discount.stripe_id if discount else None

    order.tax = tax
    order.discount = discount
    order.save()

    return order_items, tax_id, discount_id


def create_stripe_payment(order_items, tax=None, discount=None):
    currency = order_items[0].item.currency

    if currency == Currency.RUB:
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_RUB', '')
        public_key = os.environ.get('STRIPE_PUBLIC_KEY_RUB', '')

    elif currency == Currency.USD:
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY_USD', '')
        public_key = os.environ.get('STRIPE_PUBLIC_KEY_USD', '')

    else:
        raise ValueError('Invalid currency')

    line_items = []
    for order_item in order_items:
        item = order_item.item
        if item.currency != currency:
            raise ValueError('All items in order must have the same currency')
        line_item = {
            'price_data': {
                'currency': item.currency,
                'product_data': {'name': item.name},
                'unit_amount': int(round(item.price * 100)),
            },
            'quantity': order_item.quantity,
        }
        if tax:
            line_item['tax_rates'] = [tax]
        line_items.append(line_item)

    discounts = []
    if discount:
        discounts.append({'coupon': discount})

    payment_data = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'discounts': discounts,
        'mode': 'payment',
        'success_url': 'https://www.google.com/',  # Используются затычки так как обработка платежа не требуется
        'cancel_url': 'https://www.google.com/',
    }
    session = stripe.checkout.Session.create(**payment_data)

    return session, public_key
