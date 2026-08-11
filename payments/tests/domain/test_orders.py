from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currencies
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.order import Order, OrderStatus
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def test_order_create():
    test_cart = Cart()
    test_order = Order(currency=Currencies.USD, cart=test_cart)

    assert test_order.status == OrderStatus.CREATED
    assert test_order.items == []
    assert test_order.cart == test_cart
    assert test_order.currency == Currencies.USD
    assert test_order.discount is None


def test_order_create_with_discount():
    test_cart = Cart()
    test_discount = Discount(
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )
    test_order = Order(currency=Currencies.USD, cart=test_cart, discount=test_discount)

    assert test_order.discount == test_discount


def test_order_add_order_item():
    test_cart = Cart()
    test_order = Order(currency=Currencies.USD, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currencies.USD, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=Currencies.USD, price=Decimal(101.10), product=test_product_2
    )
    test_order_item_2 = OrderItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_order.add(test_order_item)
    test_order.add(test_order_item_2)

    assert len(test_order.items) == 2


def test_order_add_different_currencies_order_item():
    test_cart = Cart()
    test_order = Order(currency=Currencies.USD, cart=test_cart)

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currencies.EUR, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    test_product_2 = Product("test name 2", True)
    test_product_price_2 = ProductPrice(
        currency=Currencies.USD, price=Decimal(101.10), product=test_product_2
    )
    test_order_item_2 = OrderItem(
        product=test_product_2, product_price=test_product_price_2
    )

    test_order.add(test_order_item)
    test_order.add(test_order_item_2)

    assert len(test_order.items) == 2


def test_order_restore():
    test_cart = Cart()
    test_discount = Discount(
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )

    test_product = Product("test name", True)
    test_product_price = ProductPrice(
        currency=Currencies.USD, price=Decimal(100.10), product=test_product
    )
    test_order_item = OrderItem(product=test_product, product_price=test_product_price)

    restored = Order.restore(
        currency=Currencies.USD,
        cart=test_cart,
        items=[test_order_item],
        status=OrderStatus.PAID,
        discount=test_discount,
        id=1,
    )

    assert restored.id == 1
    assert restored.items == [test_order_item]
    assert restored.status == OrderStatus.PAID
    assert restored.cart == test_cart
    assert restored.discount == test_discount
