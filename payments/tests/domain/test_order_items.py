from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_order_item_create():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal("1.0"))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal("100.10"), product=test_product
    )
    test_order_item = OrderItem(
        product=test_product, product_price=test_product_price, order=test_order
    )

    assert test_order_item.product == test_product
    assert test_order_item.product_price == test_product_price
    assert test_order_item.order == test_order
    assert test_order_item.product_price.get_price(None) == 10010


def test_order_item_restore():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal("1.0"))
    test_cart = Cart(currency=test_currency)
    test_order = Order(currency=test_currency, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=test_currency, price=Decimal("100.10"), product=test_product
    )

    restored = OrderItem.restore(
        id=1,
        product=test_product,
        product_price=test_product_price,
        order=test_order,
    )

    assert restored.id == 1
    assert restored.product == test_product
    assert restored.product_price == test_product_price
    assert restored.order == test_order
