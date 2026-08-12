from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from payments.domain.entities.cart import Cart
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.tax import Tax


class OrderStatus(Enum):
    CREATED = "created"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class Order:
    id: int | None
    currency: Currency
    items: list[OrderItem]
    status: OrderStatus
    cart: Cart
    discount: Discount | None
    tax: Tax | None

    def __init__(
        self,
        currency: Currency,
        cart: Cart,
        discount: Discount | None = None,
        tax: Tax | None = None,
        id: int | None = None,
    ):
        self.currency = currency
        self.items = []
        self.status = OrderStatus.CREATED
        self.cart = cart
        self.discount = discount
        self.tax = tax
        self.id = id

    def add(self, item: OrderItem):
        self.items.append(item)

    def add_tax(self, tax: Tax):
        self.tax = tax

    def add_discount(self, discount: Discount):
        self.discount = discount

    def subtotal(self) -> Decimal:
        total = sum((item.price for item in self.items), Decimal("0"))
        return total.quantize(Decimal("0.01"))

    def tax_amount(self) -> Decimal:
        if self.tax is None:
            return Decimal("0.00")
        amount = self.subtotal() * self.tax.rate / 100
        return amount.quantize(Decimal("0.01"))

    def discount_amount(self) -> Decimal:
        if self.discount is None:
            return Decimal("0.00")
        subtotal = self.subtotal()
        if self.discount.type is DiscountType.PERCENTAGE:
            amount = subtotal * self.discount.value / 100
        else:
            amount = min(self.discount.value, subtotal)
        return amount.quantize(Decimal("0.01"))

    def total(self) -> Decimal:
        amount = self.subtotal() + self.tax_amount() - self.discount_amount()
        return amount.quantize(Decimal("0.01"))

    @classmethod
    def restore(
        cls,
        currency: Currency,
        cart: Cart,
        items: list[OrderItem],
        status: OrderStatus,
        discount: Discount | None = None,
        tax: Tax | None = None,
        id: int | None = None,
    ) -> Order:
        order = cls(
            currency=currency,
            cart=cart,
            discount=discount,
            tax=tax,
            id=id,
        )

        order.items = items
        order.status = status

        return order
