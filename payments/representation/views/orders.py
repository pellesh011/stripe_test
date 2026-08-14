from asgiref.sync import sync_to_async
from django.http import JsonResponse

from payments.application.use_cases.order.get_orders import GetOrdersUseCase
from payments.domain.entities.order import Order
from payments.infrastructure.database.repositories.order import OrderRepositoryImpl
from payments.infrastructure.database.repositories.payment_attempt import (
    PaymentAttemptRepositoryImpl,
)


def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status.value,
        "currency": order.currency.value,
        "subtotal": str(order.subtotal()),
        "discount_amount": str(order.discount_amount()),
        "tax_amount": str(order.tax_amount()),
        "total": str(order.total()),
        "discount": (
            {
                "id": order.discount.id,
                "name": order.discount.name,
                "type": order.discount.type.value,
                "value": str(order.discount.value),
            }
            if order.discount is not None
            else None
        ),
        "tax": (
            {
                "id": order.tax.id,
                "name": order.tax.name,
                "rate": order.tax.rate,
            }
            if order.tax is not None
            else None
        ),
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "payment_intent": (
            {
                "id": order.payment_intent,
                "client_secret": order.client_secret,
            }
            if order.payment_intent is not None
            else None
        ),
        "items": [
            {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "price": str(item.price),
                "currency": order.currency.value,
                "product_price": {
                    "id": item.product_price.id,
                    "currency": item.product_price.currency.value,
                    "price": str(item.product_price.price),
                },
            }
            for item in order.items
        ],
    }


async def get_orders(request) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse(
            {"error": "method must be GET"},
            status=405,
        )

    use_case = GetOrdersUseCase(
        orders=OrderRepositoryImpl(),
        payment_attempts=PaymentAttemptRepositoryImpl(),
    )

    orders = await sync_to_async(
        use_case.execute,
        thread_sensitive=True,
    )()

    return JsonResponse({"orders": [_serialize_order(order) for order in orders]})
