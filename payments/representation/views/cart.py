from asgiref.sync import sync_to_async
from django.http import JsonResponse

from payments.application.use_cases.cart.get_or_create_active_cart import (
    GetOrCreateActiveCartUseCase,
)
from payments.domain.entities.cart import Cart
from payments.infrastructure.database.repositories.cart import CartRepositoryImpl
from payments.infrastructure.database.uow import DjangoUnitOfWork


def _serialize_cart(cart: Cart) -> dict:
    return {
        "id": cart.id,
        "status": cart.status.value,
        "items": [
            {
                "id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "product_price_id": item.product_price.id,
                "currency": item.product_price.currency.value,
                "price": str(item.product_price.price),
            }
            for item in cart.items
        ],
    }


async def get_or_create_cart(request) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse(
            {"error": "method must be GET"},
            status=405,
        )

    use_case = GetOrCreateActiveCartUseCase(
        uow=DjangoUnitOfWork(),
        carts=CartRepositoryImpl(),
    )

    cart = await sync_to_async(
        use_case.execute,
        thread_sensitive=True,
    )()

    return JsonResponse({"cart": _serialize_cart(cart)})
