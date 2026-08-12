from decimal import Decimal

from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_product_price_create():
    test_product = Product("test name", True)
    test_exchange_rate = ExchangeRate(currency=Currency.EUR, coef=Decimal(1.1))
    test_product_price = ProductPrice(
        currency=Currency.EUR, price=Decimal(100.10), product=test_product
    )
    assert test_product_price.currency == Currency.EUR
    assert test_product_price.get_price(test_exchange_rate) == 11011


def test_product_price_default_currency():
    test_product = Product("test name", True)
    test_product_price = ProductPrice(price=Decimal("10.00"), product=test_product)
    assert test_product_price.currency == Currency.USD
