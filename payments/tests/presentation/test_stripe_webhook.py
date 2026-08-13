import json
from unittest.mock import patch

import pytest
import stripe
from django.test import Client
from django.urls import reverse

from payments.domain.entities.order import OrderStatus
from payments.domain.entities.payment import PaymentStatus
from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.infrastructure.database.models.stripe_webhook import (
    StripeWebhookEventModel,
)


@pytest.fixture
def client() -> Client:
    return Client()


def _event(event_id, event_type, intent_id):
    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": {"id": intent_id}},
    }


def _post(client, event):
    return client.post(
        reverse("stripe-webhook"),
        data=json.dumps(event),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="test_signature",
    )


def _link_attempt(payment_attempt, payment_attempt_repo, intent_id="pi_test_123"):
    payment_attempt.external_id = intent_id
    payment_attempt_repo.save(payment_attempt)


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_success(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
    order_repo,
):
    intent_id = "pi_test_123"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    mock_construct.return_value = _event("evt_1", "payment_intent.succeeded", intent_id)

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.SUCCEEDED
    )
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status is PaymentStatus.PAID
    )
    assert (
        order_repo.get_by_id(payment_attempt.payment.order.id).status
        is OrderStatus.PAID
    )

    record = StripeWebhookEventModel.objects.get(event_id="evt_1")
    assert record.event_type == "payment_intent.succeeded"
    assert record.status == "processed"
    assert record.processed_at is not None


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_payment_failed(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
):
    intent_id = "pi_test_123"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    mock_construct.return_value = _event(
        "evt_2", "payment_intent.payment_failed", intent_id
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.FAILED
    )
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.FAILED
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_canceled(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
):
    intent_id = "pi_test_123"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    mock_construct.return_value = _event("evt_3", "payment_intent.canceled", intent_id)

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.CANCELLED
    )
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.CANCELLED
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_is_idempotent(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
):
    intent_id = "pi_test_123"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    mock_construct.return_value = _event("evt_1", "payment_intent.succeeded", intent_id)

    first = _post(client, mock_construct.return_value)
    second = _post(client, mock_construct.return_value)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == {"status": "duplicate"}

    assert StripeWebhookEventModel.objects.filter(event_id="evt_1").count() == 1
    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.SUCCEEDED
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_unknown_attempt_is_handled(
    mock_construct,
    client,
):
    mock_construct.return_value = _event(
        "evt_unknown", "payment_intent.succeeded", "pi_missing"
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    record = StripeWebhookEventModel.objects.get(event_id="evt_unknown")
    assert record.status == "processed"


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_unsupported_event_is_ignored(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
):
    intent_id = "pi_test_123"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    mock_construct.return_value = _event("evt_4", "charge.refunded", intent_id)

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.CREATED
    )

    record = StripeWebhookEventModel.objects.get(event_id="evt_4")
    assert record.status == "ignored"
    assert record.processed_at is not None


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_picks_active_attempt_among_multiple(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
):
    intent_id = "pi_multi_active"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)

    failed = PaymentAttempt(
        provider=payment_attempt.provider,
        payment=payment_attempt.payment,
    )
    failed.external_id = intent_id
    failed.mark_failed()
    payment_attempt_repo.save(failed)

    mock_construct.return_value = _event(
        "evt_multi", "payment_intent.succeeded", intent_id
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.SUCCEEDED
    )
    assert (
        payment_attempt_repo.get_by_id(failed.id).status
        is PaymentAttemptStatus.FAILED
    )
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.PAID
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_ignores_event_when_attempt_succeeded(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
):
    intent_id = "pi_finished"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    payment_attempt.mark_succeeded()
    payment_attempt_repo.save(payment_attempt)

    mock_construct.return_value = _event(
        "evt_finished", "payment_intent.payment_failed", intent_id
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert (
        payment_attempt_repo.get_by_id(payment_attempt.id).status
        is PaymentAttemptStatus.SUCCEEDED
    )
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.CREATED
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_creates_new_attempt_when_all_failed(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
):
    intent_id = "pi_all_failed"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    payment_attempt.mark_failed()
    payment_attempt_repo.save(payment_attempt)

    mock_construct.return_value = _event(
        "evt_all_failed", "payment_intent.payment_failed", intent_id
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    attempts = payment_attempt_repo.get_by_payment_id(payment_attempt.payment.id)
    assert len(attempts) == 2
    assert all(item.status is PaymentAttemptStatus.FAILED for item in attempts)
    assert all(item.external_id == intent_id for item in attempts)
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.FAILED
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_creates_new_attempt_and_succeeds_after_all_failed(
    mock_construct,
    client,
    payment_attempt,
    payment_attempt_repo,
    payment_repo,
    order_repo,
):
    intent_id = "pi_retry_success"
    _link_attempt(payment_attempt, payment_attempt_repo, intent_id)
    payment_attempt.mark_failed()
    payment_attempt_repo.save(payment_attempt)

    mock_construct.return_value = _event(
        "evt_retry_success", "payment_intent.succeeded", intent_id
    )

    response = _post(client, mock_construct.return_value)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    attempts = payment_attempt_repo.get_by_payment_id(payment_attempt.payment.id)
    assert len(attempts) == 2
    assert attempts[0].status is PaymentAttemptStatus.FAILED
    assert attempts[1].status is PaymentAttemptStatus.SUCCEEDED
    assert attempts[1].external_id == intent_id
    assert (
        payment_repo.get_by_id(payment_attempt.payment.id).status
        is PaymentStatus.PAID
    )
    assert (
        order_repo.get_by_id(payment_attempt.payment.order.id).status
        is OrderStatus.PAID
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_invalid_signature_returns_400(mock_construct, client):
    mock_construct.side_effect = stripe.SignatureVerificationError(
        "Signature verification failed.",
        "test_signature",
    )

    response = _post(client, {"id": "evt_bad", "type": "payment_intent.succeeded"})

    assert response.status_code == 400
    assert response.json() == {"error": "invalid signature"}


@pytest.mark.django_db
def test_webhook_get_returns_405(client):
    response = client.get(reverse("stripe-webhook"))

    assert response.status_code == 405
