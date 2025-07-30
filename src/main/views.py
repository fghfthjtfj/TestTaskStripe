from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.http import Http404
from django.views import View
from .services.payment import *
from .models import *


class ItemDetailView(DetailView):
    model = Item
    template_name = 'main/item_page.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        prev_item = Item.objects.filter(id__lt=item.id).order_by('-id').first()
        next_item = Item.objects.filter(id__gt=item.id).order_by('id').first()
        context['prev_item'] = prev_item
        context['next_item'] = next_item
        return context


class CartManageView(View):
    def post(self, request, item_id):
        cart = request.session.get('cart', {})
        action = request.POST.get('_action', 'add')
        if action == 'delete':  # Проверка по значению (вместо def delete), потому что используется стандартная HTML-форма без JS.
            if str(item_id) in cart:
                del cart[str(item_id)]
        else:
            cart[str(item_id)] = cart.get(str(item_id), 0) + 1
        request.session['cart'] = cart
        return redirect(request.META.get('HTTP_REFERER', request.path))


class CreateOrderFromCartView(View):
    def get(self, request, pk=None):  # Сценарии покупки через корзину или сразу, обрабатываются одним view
        if pk is not None:
            cart = {str(pk): 1}
        else:
            cart = request.session.get('cart', {})
            if not cart:
                return redirect('/')

        try:
            order_items, tax_id, discount_id = write_order_data(cart)
        except ObjectDoesNotExist as e:
            return JsonResponse({'status': 'fail', 'error': f'Item does not exist {e}'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'error': f'Unexpected error {e}'}, status=500)

        try:
            session, public_key = create_stripe_payment(order_items, tax=tax_id, discount=discount_id)
        except ValueError as e:
            print(f'Payment creation failed {str(e)}')
            return JsonResponse({'status': 'fail', 'error': f'{e}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'error': f'Unexpected error: {e}'}, status=500)

        request.session.pop('cart', None)
        request.session.modified = True

        return JsonResponse({'status': 'success', 'id': session.id, 'key': public_key})


# Главной страницы на сайте нет, поэтому делаю редирект на страницу первого товара
class FirstItemRedirect(View):
    def get(self, request):
        first_item = Item.objects.order_by('id').first()
        if not first_item:
            raise Http404

        return redirect(f'/item/{first_item.id}/')
