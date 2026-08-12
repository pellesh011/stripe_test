from decimal import Decimal

import pytest
from asgiref.sync import async_to_sync

from payments.domain.entities.cart import Cart
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.payment import Payment
from payments.domain.entities.payment_attempts import PaymentAttempt
from payments.domain.entities.payment_provider import PaymentProvider
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.entities.tax import Tax
from payments.infrastructure.database.repositories.cart import CartRepositoryImpl
from payments.infrastructure.database.repositories.cart_item import (
    CartItemRepositoryImpl,
)
from payments.infrastructure.database.repositories.discount import (
    DiscountRepositoryImpl,
)
from payments.infrastructure.database.repositories.exchange_rate import (
    ExchangeRateRepositoryImpl,
)
from payments.infrastructure.database.repositories.order import OrderRepositoryImpl
from payments.infrastructure.database.repositories.order_item import (
    OrderItemRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment import (
    PaymentRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment_attempt import (
    PaymentAttemptRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment_provider import (
    PaymentProviderRepositoryImpl,
)
from payments.infrastructure.database.repositories.product import (
    ProductRepositoryImpl,
)
from payments.infrastructure.database.repositories.product_price import (
    ProductPriceRepositoryImpl,
)
from payments.infrastructure.database.repositories.tax import TaxRepositoryImpl


@pytest.fixture
def call():
    return async_to_sync


@pytest.fixture
def exchange_rate_repo() -> ExchangeRateRepositoryImpl:
    return ExchangeRateRepositoryImpl()


@pytest.fixture
def discount_repo() -> DiscountRepositoryImpl:
    return DiscountRepositoryImpl()


@pytest.fixture
def tax_repo() -> TaxRepositoryImpl:
    return TaxRepositoryImpl()


@pytest.fixture
def product_repo() -> ProductRepositoryImpl:
    return ProductRepositoryImpl()


@pytest.fixture
def product_price_repo() -> ProductPriceRepositoryImpl:
    return ProductPriceRepositoryImpl()


@pytest.fixture
def cart_repo() -> CartRepositoryImpl:
    return CartRepositoryImpl()


@pytest.fixture
def cart_item_repo() -> CartItemRepositoryImpl:
    return CartItemRepositoryImpl()


@pytest.fixture
def order_repo() -> OrderRepositoryImpl:
    return OrderRepositoryImpl()


@pytest.fixture
def order_item_repo() -> OrderItemRepositoryImpl:
    return OrderItemRepositoryImpl()


@pytest.fixture
def payment_repo() -> PaymentRepositoryImpl:
    return PaymentRepositoryImpl()


@pytest.fixture
def payment_attempt_repo() -> PaymentAttemptRepositoryImpl:
    return PaymentAttemptRepositoryImpl()


@pytest.fixture
def payment_provider_repo() -> PaymentProviderRepositoryImpl:
    return PaymentProviderRepositoryImpl()


@pytest.fixture
def exchange_rate(exchange_rate_repo, db, call) -> ExchangeRate:
    entity = ExchangeRate(currency=Currency.EUR, coef=Decimal("1.10"))
    call(exchange_rate_repo.save)(entity)
    return entity


@pytest.fixture
def discount(discount_repo, db, call) -> Discount:
    entity = Discount(
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )
    call(discount_repo.save)(entity)
    return entity


@pytest.fixture
def inactive_discount(discount_repo, db, call) -> Discount:
    entity = Discount(
        name="Inactive Discount",
        type=DiscountType.FIXED,
        value=Decimal("5.00"),
        is_active=False,
    )
    call(discount_repo.save)(entity)
    return entity


@pytest.fixture
def tax(tax_repo, db, call) -> Tax:
    entity = Tax(name="VAT", rate=20)
    call(tax_repo.save)(entity)
    return entity


@pytest.fixture
def product(product_repo, db, call) -> Product:
    entity = Product(name="Test Product", is_active=True)
    call(product_repo.save)(entity)
    return entity


@pytest.fixture
def inactive_product(product_repo, db, call) -> Product:
    entity = Product(name="Inactive Product", is_active=False)
    call(product_repo.save)(entity)
    return entity


@pytest.fixture
def product_price(product_price_repo, product, db, call) -> ProductPrice:
    entity = ProductPrice(
        currency=Currency.EUR, price=Decimal("10.00"), product=product
    )
    call(product_price_repo.save)(entity)
    return entity


@pytest.fixture
def payment_provider(payment_provider_repo, db, call) -> PaymentProvider:
    entity = PaymentProvider(id=None, name="test-provider")
    call(payment_provider_repo.save)(entity)
    return entity


@pytest.fixture
def cart(cart_repo, db, call) -> Cart:
    entity = Cart()
    call(cart_repo.save)(entity)
    return entity


@pytest.fixture
def cart_item(cart_item_repo, cart, product, product_price, db, call) -> CartItem:
    entity = CartItem(product=product, product_price=product_price, cart=cart)
    call(cart_item_repo.save)(entity)
    return entity


@pytest.fixture
def order(order_repo, cart, discount, db) -> Order:
    entity = Order(currency=Currency.EUR, cart=cart, discount=discount)
    order_repo.save(entity)
    return entity


@pytest.fixture
def order_item(
    order_item_repo, order, product, product_price, exchange_rate, db
) -> OrderItem:
    entity = OrderItem(
        product=product,
        product_price=product_price,
        exchange_rate=exchange_rate,
        price=product_price.price * exchange_rate.coef,
        order=order,
    )
    order_item_repo.save(entity)
    return entity


@pytest.fixture
def payment(payment_repo, order, db) -> Payment:
    entity = Payment(order=order, amount=Decimal("10.00"), currency=Currency.EUR)
    payment_repo.save(entity)
    return entity


@pytest.fixture
def payment_attempt(
    payment_attempt_repo,
    payment,
    payment_provider,
    db,
) -> PaymentAttempt:
    entity = PaymentAttempt(provider=payment_provider, payment=payment)
    payment_attempt_repo.save(entity)
    return entity
