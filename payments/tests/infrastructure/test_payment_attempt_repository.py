import pytest

from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(payment_attempt_repo):
    with pytest.raises(EntityNotFoundError):
        payment_attempt_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(
    payment_attempt_repo,
    payment,
    payment_provider,
):
    entity = PaymentAttempt(provider=payment_provider, payment=payment)
    assert entity.id is None

    payment_attempt_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_full_aggregate(
    payment_attempt_repo,
    payment_attempt,
):
    assert payment_attempt.id is not None
    loaded = payment_attempt_repo.get_by_id(payment_attempt.id)

    assert loaded.id == payment_attempt.id
    assert loaded.status is PaymentAttemptStatus.CREATED
    assert loaded.provider.id == payment_attempt.provider.id
    assert loaded.payment.id == payment_attempt.payment.id
    assert loaded.payment.order.id == payment_attempt.payment.order.id


@pytest.mark.django_db
def test_get_by_payment_id(payment_attempt_repo, payment_attempt, payment):
    assert payment.id is not None
    attempts = payment_attempt_repo.get_by_payment_id(payment.id)

    assert len(attempts) == 1
    assert attempts[0].id == payment_attempt.id


@pytest.mark.django_db
def test_get_by_payment_id_pagination_limit_and_offset(
    payment_attempt_repo,
    payment,
    payment_provider,
):
    for _ in range(3):
        entity = PaymentAttempt(provider=payment_provider, payment=payment)
        payment_attempt_repo.save(entity)

    assert payment.id is not None
    first_page = payment_attempt_repo.get_by_payment_id(payment.id, limit=2, offset=0)
    second_page = payment_attempt_repo.get_by_payment_id(payment.id, limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 1

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.django_db
def test_save_persists_status_and_completed_at(
    payment_attempt_repo,
    payment_attempt,
):
    assert payment_attempt.id is not None
    payment_attempt.mark_succeeded()

    payment_attempt_repo.save(payment_attempt)

    loaded = payment_attempt_repo.get_by_id(payment_attempt.id)
    assert loaded.status is PaymentAttemptStatus.SUCCEEDED
    assert loaded.completed_at is not None
