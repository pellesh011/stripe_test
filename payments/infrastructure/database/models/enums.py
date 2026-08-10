from django.db import models

from payments.domain.entities.cart import CartStatus
from payments.domain.entities.currency import Currencies
from payments.domain.entities.order import OrderStatus

class CurrencyChoices(models.TextChoices):
    USD = Currencies.USD.value, "USD"
    RUB = Currencies.RUB.value, "RUB"
    EUR = Currencies.EUR.value, "EUR"


class OrderStatusChoices(models.TextChoices):
    CREATED = OrderStatus.CREATED.value, "Created"
    PENDING_PAYMENT = OrderStatus.PENDING_PAYMENT.value, "Pending payment"
    PAID = OrderStatus.PAID.value, "Paid"
    PROCESSING = OrderStatus.PROCESSING.value, "Processing"
    SHIPPED = OrderStatus.SHIPPED.value, "Shipped"
    COMPLETED = OrderStatus.COMPLETED.value, "Completed"
    CANCELLED = OrderStatus.CANCELLED.value, "Cancelled"
    REFUNDED = OrderStatus.REFUNDED.value, "Refunded"


class CartStatusChoices(models.TextChoices):
    ACTIVE = CartStatus.ACTIVE.value, "Active"
    CHECKOUT = CartStatus.CHECKOUT.value, "Checkout"
    CONVERTED = CartStatus.CONVERTED.value, "Converted"
    ABANDONED = CartStatus.ABANDONED.value, "Abandoned"
    EXPIRED = CartStatus.EXPIRED.value, "Expired"