from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_order_item_create():
    test_exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal("1.0"))
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currency.USD, price=Decimal("100.10"), product=test_product
    )
    test_order_item = OrderItem(
        product=test_product,
        product_price=test_product_price,
        exchange_rate=test_exchange_rate,
        price=test_product_price.price * test_exchange_rate.coef,
        order=test_order,
    )

    assert test_order_item.product == test_product
    assert test_order_item.product_price == test_product_price
    assert test_order_item.exchange_rate == test_exchange_rate
    assert test_order_item.price == Decimal("100.10")
    assert test_order_item.order == test_order
    assert test_order_item.product_price.get_price(test_exchange_rate) == 10010


def test_order_item_restore():
    test_exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal("1.0"))
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currency.USD, price=Decimal("100.10"), product=test_product
    )

    restored = OrderItem.restore(
        id=1,
        product=test_product,
        product_price=test_product_price,
        exchange_rate=test_exchange_rate,
        price=test_product_price.price * test_exchange_rate.coef,
        order=test_order,
    )

    assert restored.id == 1
    assert restored.product == test_product
    assert restored.product_price == test_product_price
    assert restored.exchange_rate == test_exchange_rate
    assert restored.price == Decimal("100.10")
    assert restored.order == test_order
