import logging

import stripe
from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from payments.application.dto.payment_webhook import PaymentWebhookDTO
from payments.application.use_cases.payment.process_payment_webhook import (
    SUPPORTED_EVENT_TYPES,
    ProcessPaymentWebhookUseCase,
)
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.cart import CartRepository
from payments.infrastructure.database.models.stripe_webhook import (
    StripeWebhookEventModel,
)
from payments.infrastructure.database.repositories.cart import CartRepositoryImpl
from payments.infrastructure.database.repositories.order import OrderRepositoryImpl
from payments.infrastructure.database.repositories.payment import (
    PaymentRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment_attempt import (
    PaymentAttemptRepositoryImpl,
)
from payments.infrastructure.database.uow import DjangoUnitOfWork

logger = logging.getLogger(__name__)

_WEBHOOK_EVENT_STATUS_PROCESSED = "processed"
_WEBHOOK_EVENT_STATUS_FAILED = "failed"
_WEBHOOK_EVENT_STATUS_IGNORED = "ignored"


@csrf_exempt
async def stripe_webhook(request) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse(
            {"error": "method must be POST"},
            status=405,
        )

    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature"),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError) as exc:
        logger.warning(
            "Stripe webhook signature verification failed: %s",
            exc,
        )
        return JsonResponse(
            {"error": "invalid signature"},
            status=400,
        )

    event_id = event["id"]
    event_type = event["type"]

    _, created = await sync_to_async(
        StripeWebhookEventModel.objects.get_or_create, thread_sensitive=True
    )(
        event_id=event_id,
        defaults={
            "event_type": event_type,
            "status": "received",
        },
    )
    if not created:
        return JsonResponse({"status": "duplicate"})

    if event_type not in SUPPORTED_EVENT_TYPES:
        await sync_to_async(
            StripeWebhookEventModel.objects.filter(event_id=event_id).update,
            thread_sensitive=True,
        )(
            status=_WEBHOOK_EVENT_STATUS_IGNORED,
            processed_at=timezone.now(),
        )
        return JsonResponse({"status": "ignored"})

    use_case = ProcessPaymentWebhookUseCase(
        uow=DjangoUnitOfWork(),
        carts=CartRepositoryImpl(),
        payment_attempts=PaymentAttemptRepositoryImpl(),
        payments=PaymentRepositoryImpl(),
        orders=OrderRepositoryImpl(),
    )

    try:
        await sync_to_async(
            use_case.execute,
            thread_sensitive=True,
        )(
            PaymentWebhookDTO(
                event_id=event_id,
                event_type=event_type,
                payment_intent_id=event["data"]["object"]["id"],
            )
        )
    except EntityNotFoundError:
        await sync_to_async(
            StripeWebhookEventModel.objects.filter(event_id=event_id).update,
            thread_sensitive=True,
        )(
            status=_WEBHOOK_EVENT_STATUS_PROCESSED,
            processed_at=timezone.now(),
        )
        return JsonResponse({"status": "ok"})
    except Exception:
        await sync_to_async(
            StripeWebhookEventModel.objects.filter(event_id=event_id).update,
            thread_sensitive=True,
        )(
            status=_WEBHOOK_EVENT_STATUS_FAILED,
        )
        logger.exception(
            "Stripe webhook processing failed: event_id=%s event_type=%s",
            event_id,
            event_type,
        )
        return JsonResponse(
            {"error": "internal error"},
            status=500,
        )

    await sync_to_async(
        StripeWebhookEventModel.objects.filter(event_id=event_id).update,
        thread_sensitive=True,
    )(
        status=_WEBHOOK_EVENT_STATUS_PROCESSED,
        processed_at=timezone.now(),
    )
    return JsonResponse({"status": "ok"})
