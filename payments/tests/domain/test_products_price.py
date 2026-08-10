from decimal import Decimal

from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_product_price_create():
    test_product = Product("test name", True)
    test_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal(100.10), product=test_product
    )
    assert test_product_price.currency.currency == Currencies.EUR
    assert test_product_price.get_price(None) == 11011
