from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import Order, OrderStatus
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice


def _make_order_item(product_name: str, price: Decimal) -> OrderItem:
    product = Product(product_name, True)
    product_price = ProductPrice(currency=Currency.USD, price=price, product=product)
    exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal("1.0"))
    return OrderItem(
        product=product,
        product_price=product_price,
        exchange_rate=exchange_rate,
        price=price * exchange_rate.coef,
    )


def test_order_create():
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    assert test_order.status == OrderStatus.CREATED
    assert test_order.items == []
    assert test_order.cart == test_cart
    assert test_order.currency == Currency.USD
    assert test_order.discount is None


def test_order_create_with_discount():
    test_cart = Cart()
    test_discount = Discount(
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )
    test_order = Order(currency=Currency.USD, cart=test_cart, discount=test_discount)

    assert test_order.discount == test_discount


def test_order_add_order_item():
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    test_order_item = _make_order_item("test name", Decimal("100.10"))
    test_order_item_2 = _make_order_item("test name 2", Decimal("101.10"))

    test_order.add(test_order_item)
    test_order.add(test_order_item_2)

    assert len(test_order.items) == 2


def test_order_add_different_currencies_order_item():
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    product = Product("test name", True)
    product_price = ProductPrice(
        currency=Currency.EUR, price=Decimal("100.10"), product=product
    )
    exchange_rate = ExchangeRate(currency=Currency.EUR, coef=Decimal("1.10"))
    test_order_item = OrderItem(
        product=product,
        product_price=product_price,
        exchange_rate=exchange_rate,
        price=product_price.price * exchange_rate.coef,
    )

    test_order_item_2 = _make_order_item("test name 2", Decimal("101.10"))

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

    test_order_item = _make_order_item("test name", Decimal("100.10"))

    restored = Order.restore(
        currency=Currency.USD,
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
