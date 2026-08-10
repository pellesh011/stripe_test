from decimal import Decimal

from payments.domain.entities.currency import Currency
from payments.domain.entities.product import Product


class ProductPrice:
    currency: Currency
    price: Decimal
    product: Product
    is_active: bool

    def __init__(self, currency: Currency, price: Decimal, product: Product):
        self.currency = currency
        self.price = price
        self.is_active = True
        self.product = product

    def set_active(self, is_active: bool) -> bool:
        self.is_active = is_active
        return self.is_active

    def get_price(self, currency: Currency | None) -> int:
        _currency = currency or self.currency
        return int(self.price * _currency.coef * 100)
