from datetime import UTC, datetime
from decimal import Decimal

from payments.domain.entities.cart import Cart
from payments.domain.entities.currency import Currencies, Currency
from payments.domain.entities.order import Order
from payments.domain.entities.payment import Payment
from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.domain.entities.payment_provider import PaymentProvider


def make_payment_attempt() -> PaymentAttempt:
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart()
    test_order = Order(currency=Currencies.USD, cart=test_cart)
    test_payment = Payment(
        order=test_order, amount=Decimal("10.00"), currency=test_currency
    )
    test_provider = PaymentProvider(id=None, name="test-provider")
    return PaymentAttempt(provider=test_provider, payment=test_payment)


def test_payment_attempt_create():
    test_attempt = make_payment_attempt()

    assert test_attempt.id is None
    assert test_attempt.external_id is None
    assert test_attempt.status == PaymentAttemptStatus.CREATED
    assert test_attempt.completed_at is None
    assert isinstance(test_attempt.created_at, datetime)


def test_payment_attempt_mark_processing():
    test_attempt = make_payment_attempt()

    test_attempt.mark_processing()

    assert test_attempt.status == PaymentAttemptStatus.PROCESSING
    assert test_attempt.completed_at is None


def test_payment_attempt_mark_succeeded():
    test_attempt = make_payment_attempt()

    test_attempt.mark_succeeded()

    assert test_attempt.status == PaymentAttemptStatus.SUCCEEDED
    assert test_attempt.completed_at is not None


def test_payment_attempt_mark_failed():
    test_attempt = make_payment_attempt()

    test_attempt.mark_failed()

    assert test_attempt.status == PaymentAttemptStatus.FAILED
    assert test_attempt.completed_at is not None


def test_payment_attempt_mark_cancelled():
    test_attempt = make_payment_attempt()

    test_attempt.mark_cancelled()

    assert test_attempt.status == PaymentAttemptStatus.CANCELLED
    assert test_attempt.completed_at is not None


def test_payment_attempt_restore():
    test_currency = Currency(currency=Currencies.USD, coef=Decimal(1.0))
    test_cart = Cart()
    test_order = Order(currency=Currencies.USD, cart=test_cart)
    test_payment = Payment(
        order=test_order, amount=Decimal("10.00"), currency=test_currency
    )
    test_provider = PaymentProvider(id=1, name="test-provider")

    created_at = datetime(2024, 1, 1, tzinfo=UTC)
    completed_at = datetime(2024, 1, 2, tzinfo=UTC)

    restored = PaymentAttempt.restore(
        id=1,
        external_id="ext-123",
        provider=test_provider,
        payment=test_payment,
        status=PaymentAttemptStatus.SUCCEEDED,
        created_at=created_at,
        completed_at=completed_at,
    )

    assert restored.id == 1
    assert restored.external_id == "ext-123"
    assert restored.provider == test_provider
    assert restored.payment == test_payment
    assert restored.status == PaymentAttemptStatus.SUCCEEDED
    assert restored.created_at == created_at
    assert restored.completed_at == completed_at
