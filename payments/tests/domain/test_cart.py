from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_cart_create():
    test_cart = Cart()
    assert isinstance(test_cart, Cart)


def test_cart_add_cart_items():
    test_cart = Cart()

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currency.EUR, price=Decimal(100.10), product=test_product
    )

    test_cart_item = CartItem(product=test_product, product_price=test_product_price)
    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=Currency.EUR, price=Decimal(101.10), product=test_product_2
    )

    test_cart_item_2 = CartItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_cart.add(test_cart_item)
    test_cart.add(test_cart_item_2)

    assert len(test_cart.items) == 2


def test_cart_add_different_currencies_cart_items():
    test_cart = Cart()

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currency.EUR, price=Decimal(100.10), product=test_product
    )

    test_cart_item = CartItem(product=test_product, product_price=test_product_price)

    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=Currency.USD, price=Decimal(101.10), product=test_product_2
    )

    test_cart_item_2 = CartItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_cart.add(test_cart_item)
    test_cart.add(test_cart_item_2)

    assert len(test_cart.items) == 2
