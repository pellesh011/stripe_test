from decimal import Decimal

import pytest

from payments.domain.entities.payment import Payment, PaymentStatus
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(payment_repo):
    with pytest.raises(EntityNotFoundError):
        payment_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(payment_repo, order, exchange_rate):
    entity = Payment(order=order, amount=Decimal("25.00"), currency=exchange_rate)
    assert entity.id is None

    payment_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_full_aggregate(payment_repo, payment):
    assert payment.id is not None
    loaded = payment_repo.get_by_id(payment.id)

    assert loaded.id == payment.id
    assert loaded.amount == Decimal("10.00")
    assert loaded.status is PaymentStatus.CREATED
    assert loaded.currency.currency == payment.currency.currency
    assert loaded.order.id == payment.order.id
    assert loaded.order.cart.id == payment.order.cart.id


@pytest.mark.django_db
def test_get_by_order_id(payment_repo, payment):
    assert payment.order.id is not None
    loaded = payment_repo.get_by_order_id(payment.order.id)

    assert loaded.id == payment.id


@pytest.mark.django_db
def test_get_by_order_id_returns_latest(payment_repo, order, exchange_rate):
    assert order.id is not None
    first = Payment(order=order, amount=Decimal("1.00"), currency=exchange_rate)
    payment_repo.save(first)
    second = Payment(order=order, amount=Decimal("2.00"), currency=exchange_rate)
    payment_repo.save(second)

    loaded = payment_repo.get_by_order_id(order.id)

    assert loaded.id == second.id


@pytest.mark.django_db
def test_get_by_order_id_not_found(payment_repo, order):
    assert order.id is not None
    with pytest.raises(EntityNotFoundError):
        payment_repo.get_by_order_id(order.id)


@pytest.mark.django_db
def test_save_update_status(payment_repo, payment):
    assert payment.id is not None
    payment.set_status(PaymentStatus.PENDING)

    payment_repo.save(payment)

    loaded = payment_repo.get_by_id(payment.id)
    assert loaded.status is PaymentStatus.PENDING
