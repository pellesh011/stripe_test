from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.product import Product


class ProductPrice:
    id: int | None
    currency: Currency
    price: Decimal
    product: Product
    is_active: bool

    def __init__(
        self,
        price: Decimal,
        product: Product,
        currency: Currency = Currency.USD,
        id: int | None = None,
    ):
        self.currency = currency
        self.price = price
        self.is_active = True
        self.product = product
        self.id = id

    def set_active(self, is_active: bool) -> bool:
        self.is_active = is_active
        return self.is_active

    def get_price(self, currency: ExchangeRate) -> int:
        return int(self.price * currency.coef * 100)

    @classmethod
    def restore(
        cls,
        price: Decimal,
        product: Product,
        is_active: bool,
        currency: Currency = Currency.USD,
        id: int | None = None,
    ) -> ProductPrice:
        product_price = cls(price=price, product=product, currency=currency, id=id)
        product_price.is_active = is_active
        return product_price
