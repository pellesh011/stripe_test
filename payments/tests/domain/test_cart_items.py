from decimal import Decimal

from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_cart_items_create():
    test_exchange_rate = ExchangeRate(currency=Currency.EUR, coef=Decimal(1.1))
    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currency.EUR, price=Decimal(100.10), product=test_product
    )

    test_cart_item = CartItem(product=test_product, product_price=test_product_price)

    assert test_cart_item.product.name == "test name"
    assert test_cart_item.product_price.get_price(test_exchange_rate) == 11011
