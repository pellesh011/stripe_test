from decimal import Decimal

import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import ProductCurrencyError


def test_cart_create():
    test_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_cart = Cart(currency=test_currency)
    assert isinstance(test_cart, Cart)


def test_cart_add_cart_items():
    test_cart_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_cart = Cart(currency=test_cart_currency)

    test_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal(100.10), product=test_product
    )

    test_cart_item = CartItem(product=test_product, product_price=test_product_price)
    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=test_currency, price=Decimal(101.10), product=test_product_2
    )

    test_cart_item_2 = CartItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_cart.add(test_cart_item)
    test_cart.add(test_cart_item_2)

    assert len(test_cart.items) == 2


def test_cart_add_different_currencies_cart_items():
    test_cart_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart(currency=test_cart_currency)

    test_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal(100.10), product=test_product
    )

    test_cart_item = CartItem(product=test_product, product_price=test_product_price)

    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=test_currency, price=Decimal(101.10), product=test_product_2
    )

    test_cart_item_2 = CartItem(
        product=test_product_2, product_price=test_product_price_2
    )

    with pytest.raises(ProductCurrencyError):
        test_cart.add(test_cart_item)

    test_cart.add(test_cart_item_2)

    assert len(test_cart.items) == 1
