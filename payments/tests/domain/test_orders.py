from decimal import Decimal

import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.order import Order, OrderStatus
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import ProductCurrencyError


def test_order_create():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    assert test_order.status == OrderStatus.CREATED
    assert test_order.items == []
    assert test_order.cart == test_cart
    assert test_order.currency == test_currency


def test_order_add_order_item():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=test_currency, price=Decimal(101.10), product=test_product_2
    )
    test_order_item_2 = OrderItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_order.add(test_order_item)
    test_order.add(test_order_item_2)

    assert len(test_order.items) == 2


def test_order_add_different_currencies_order_item():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    other_currency = Currency(currency=Currencies.EUR, coef=Decimal(1.1))
    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=other_currency, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    with pytest.raises(ProductCurrencyError):
        test_order.add(test_order_item)

    assert test_order.items == []


def test_order_restore():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    restored = Order.restore(
        currency=test_currency,
        cart=test_cart,
        items=[test_order_item],
        status=OrderStatus.PAID,
        id=1,
    )

    assert restored.id == 1
    assert restored.items == [test_order_item]
    assert restored.status == OrderStatus.PAID
    assert restored.cart == test_cart
