from asgiref.sync import sync_to_async
from django.http import JsonResponse

from payments.application.use_cases.order.get_orders import GetOrdersUseCase
from payments.domain.entities.order import Order
from payments.infrastructure.database.repositories.order import OrderRepositoryImpl


def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status.value,
        "currency": order.currency.value,
        "total": str(order.total()),
        "items": [
            {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "price": str(item.price),
                "currency": item.product_price.currency.value,
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
    )

    orders = await sync_to_async(
        use_case.execute,
        thread_sensitive=True,
    )()

    return JsonResponse({"orders": [_serialize_order(order) for order in orders]})
