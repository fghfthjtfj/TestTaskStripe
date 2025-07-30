from django.db import models


class Currency(models.TextChoices):
    RUB = 'rub', 'рубль'
    USD = 'usd', 'доллар'


class OrderModifier(models.Model):
    name = models.CharField(max_length=100)
    stripe_id = models.CharField()
    currency = models.CharField(choices=Currency.choices, default=Currency.RUB)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Discount(OrderModifier):
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


class Tax(OrderModifier):
    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'


class Item(models.Model):
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    currency = models.CharField(choices=Currency.choices, default=Currency.RUB)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Значение налога в платёжке применяется к товарам, а не всей корзине. Но в упрощённом примере, я просто копирую это значение к товарам
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, blank=True, null=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('order', 'item')

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
