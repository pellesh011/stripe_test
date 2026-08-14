import json

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from payments.application.dto.cart import AddToCartDTO
from payments.application.use_cases.cart.add_to_cart import AddToCartUseCase
from payments.application.use_cases.cart.get_or_create_active_cart import (
    GetOrCreateActiveCartUseCase,
)
from payments.domain.entities.cart import Cart
from payments.domain.exceptions import (
    CartNotActiveError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)
from payments.infrastructure.database.repositories.cart import CartRepositoryImpl
from payments.infrastructure.database.repositories.cart_item import (
    CartItemRepositoryImpl,
)
from payments.infrastructure.database.repositories.product import (
    ProductRepositoryImpl,
)
from payments.infrastructure.database.repositories.product_price import (
    ProductPriceRepositoryImpl,
)
from payments.infrastructure.database.uow import DjangoUnitOfWork

_ADD_TO_CART_ERRORS: dict[type[Exception], tuple[int, str]] = {
    EntityNotFoundError: (404, "Entity not found"),
    CartNotActiveError: (400, "Cart is not active"),
    ProductNotActiveError: (400, "Product is not active"),
    ProductPriceNotActiveError: (400, "Product price is not active"),
}


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


def _parse_required_id(data, field: str) -> tuple[int | None, str | None]:
    raw = data.get(field)
    if raw is None:
        return None, f"{field} is required"
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw, None
    return None, f"{field} must be an integer"


@csrf_exempt
async def add_to_cart(request) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse(
            {"error": "method must be POST"},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError, UnicodeDecodeError:
        return JsonResponse(
            {"error": "invalid JSON body"},
            status=400,
        )
    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "body must be a JSON object"},
            status=400,
        )

    product_id, error = _parse_required_id(data, "product_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)
    assert product_id is not None

    product_price_id, error = _parse_required_id(data, "product_price_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)
    assert product_price_id is not None

    cart_id, error = _parse_required_id(data, "cart_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)
    assert cart_id is not None

    use_case = AddToCartUseCase(
        uow=DjangoUnitOfWork(),
        carts=CartRepositoryImpl(),
        cart_items=CartItemRepositoryImpl(),
        products=ProductRepositoryImpl(),
        product_prices=ProductPriceRepositoryImpl(),
    )

    try:
        item = await sync_to_async(
            use_case.execute,
            thread_sensitive=True,
        )(
            AddToCartDTO(
                product_id=product_id,
                product_price_id=product_price_id,
                cart_id=cart_id,
            )
        )
    except tuple(_ADD_TO_CART_ERRORS) as exc:
        status, message = _ADD_TO_CART_ERRORS[type(exc)]
        return JsonResponse({"error": message}, status=status)

    cart_id = item.cart.get_id() if item.cart is not None else cart_id
    cart = await sync_to_async(CartRepositoryImpl().get_by_id)(
        cart_id,
    )
    return JsonResponse({"cart": _serialize_cart(cart)})


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
