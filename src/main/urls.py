from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path('', FirstItemRedirect.as_view(), name='home'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('item/add/<int:item_id>/', CartManageView.as_view(), name='cart_manage'),
    path('buy/', CreateOrderFromCartView.as_view(), name='item_buy'),
    path('buy/<int:pk>/', CreateOrderFromCartView.as_view(), name='cart_buy')

]
