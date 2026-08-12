from decimal import Decimal

import pytest

from payments.domain.entities.cart import Cart
from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.entities.order import Order
from payments.domain.entities.payment import Payment, PaymentStatus
from payments.domain.exceptions import InvalidPaymentStatusTransition


def make_payment() -> Payment:
    test_exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal(1.0))
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)
    return Payment(
        order=test_order,
        amount=Decimal("10.00"),
        currency=test_exchange_rate,
    )


def payment_in_state(status: PaymentStatus) -> Payment:
    path = {
        PaymentStatus.CREATED: [],
        PaymentStatus.PENDING: [PaymentStatus.PENDING],
        PaymentStatus.CANCELLED: [PaymentStatus.CANCELLED],
        PaymentStatus.PAID: [PaymentStatus.PENDING, PaymentStatus.PAID],
        PaymentStatus.FAILED: [PaymentStatus.PENDING, PaymentStatus.FAILED],
        PaymentStatus.REFUNDED: [
            PaymentStatus.PENDING,
            PaymentStatus.PAID,
            PaymentStatus.REFUNDED,
        ],
    }
    test_payment = make_payment()
    for next_status in path[status]:
        test_payment.set_status(next_status)
    return test_payment


def test_payment_create():
    test_exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal(1.0))
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    test_payment = Payment(
        order=test_order, amount=Decimal("10.00"), currency=test_exchange_rate
    )

    assert test_payment.status == PaymentStatus.CREATED
    assert test_payment.order == test_order
    assert test_payment.amount == Decimal("10.00")
    assert test_payment.currency == test_exchange_rate
    assert test_payment.id is None


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PaymentStatus.CREATED, PaymentStatus.PENDING),
        (PaymentStatus.CREATED, PaymentStatus.CANCELLED),
        (PaymentStatus.PENDING, PaymentStatus.PAID),
        (PaymentStatus.PENDING, PaymentStatus.FAILED),
        (PaymentStatus.PENDING, PaymentStatus.CANCELLED),
        (PaymentStatus.PAID, PaymentStatus.REFUNDED),
        (PaymentStatus.FAILED, PaymentStatus.PENDING),
    ],
)
def test_payment_valid_status_transition(current, target):
    test_payment = payment_in_state(current)

    test_payment.set_status(target)

    assert test_payment.status == target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PaymentStatus.CREATED, PaymentStatus.PAID),
        (PaymentStatus.CREATED, PaymentStatus.FAILED),
        (PaymentStatus.CREATED, PaymentStatus.REFUNDED),
        (PaymentStatus.PENDING, PaymentStatus.REFUNDED),
        (PaymentStatus.PAID, PaymentStatus.PENDING),
        (PaymentStatus.PAID, PaymentStatus.CANCELLED),
        (PaymentStatus.FAILED, PaymentStatus.PAID),
        (PaymentStatus.FAILED, PaymentStatus.CANCELLED),
        (PaymentStatus.CANCELLED, PaymentStatus.PENDING),
        (PaymentStatus.CANCELLED, PaymentStatus.PAID),
        (PaymentStatus.REFUNDED, PaymentStatus.PAID),
        (PaymentStatus.REFUNDED, PaymentStatus.CANCELLED),
    ],
)
def test_payment_invalid_status_transition(current, target):
    test_payment = payment_in_state(current)

    with pytest.raises(InvalidPaymentStatusTransition):
        test_payment.set_status(target)

    assert test_payment.status == current


def test_payment_restore():
    test_exchange_rate = ExchangeRate(currency=Currency.USD, coef=Decimal(1.0))
    test_cart = Cart()
    test_order = Order(currency=Currency.USD, cart=test_cart)

    restored = Payment.restore(
        id=1,
        order=test_order,
        amount=Decimal("10.00"),
        currency=test_exchange_rate,
        status=PaymentStatus.PAID,
    )

    assert restored.id == 1
    assert restored.order == test_order
    assert restored.amount == Decimal("10.00")
    assert restored.currency == test_exchange_rate
    assert restored.status == PaymentStatus.PAID
