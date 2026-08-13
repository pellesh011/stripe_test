from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.product import Product


class ProductPrice:
    _id: int | None
    _currency: Currency
    _price: Decimal
    _product: Product
    _is_active: bool

    __slots__ = (
        "_currency",
        "_id",
        "_is_active",
        "_price",
        "_product",
    )

    def __init__(
        self,
        price: Decimal,
        product: Product,
        currency: Currency = Currency.USD,
        id: int | None = None,
    ):
        object.__setattr__(self, "_id", id)
        object.__setattr__(self, "_currency", currency)
        object.__setattr__(self, "_price", price)
        object.__setattr__(self, "_product", product)
        object.__setattr__(self, "_is_active", True)

    def __setattr__(self, name, value):
        if name == "id":
            object.__setattr__(self, "_id", value)
        else:
            raise AttributeError(f"{type(self).__name__}.{name} is immutable")

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def product(self) -> Product:
        return self._product

    @property
    def is_active(self) -> bool:
        return self._is_active

    def set_active(self, is_active: bool) -> bool:
        object.__setattr__(self, "_is_active", is_active)
        return self._is_active

    def get_price(self, currency: ExchangeRate) -> int:
        return int(self._price * currency.coef * 100)

    @classmethod
    def restore(
        cls,
        price: Decimal,
        product: Product,
        is_active: bool,
        currency: Currency = Currency.USD,
        id: int | None = None,
    ) -> ProductPrice:
        product_price = cls(
            price=price,
            product=product,
            currency=currency,
            id=id,
        )

        product_price.set_active(is_active)

        return product_price
