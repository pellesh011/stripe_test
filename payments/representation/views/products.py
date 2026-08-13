from asgiref.sync import sync_to_async
from django.http import JsonResponse

from payments.application.dto.product import GetProductListDTO, PaginationDTO
from payments.application.use_cases.product.get_product_list import (
    GetProductListUseCase,
)
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.product import Product
from payments.infrastructure.database.repositories.product import (
    ProductRepositoryImpl,
)
from payments.infrastructure.database.repositories.product_price import (
    ProductPriceRepositoryImpl,
)


def _serialize_product(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "is_active": product.is_active,
        "prices": [
            {
                "id": price.id,
                "currency": price.currency.value,
                "price": str(price.price),
                "is_active": price.is_active,
            }
            for price in product.prices
        ],
    }


def _parse_pagination(data, parameter: str, default: int) -> int | None:
    raw = data.get(parameter)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return None
    if value < 0:
        return None
    return value


async def get_product_list(request) -> JsonResponse:
    limit = _parse_pagination(request.GET, "limit", 10)
    offset = _parse_pagination(request.GET, "offset", 0)
    if limit is None or offset is None:
        return JsonResponse(
            {"error": "limit and offset must be non-negative integers"},
            status=400,
        )

    currency = request.GET.get("currency") or None
    if currency is not None and currency not in {item.value for item in Currency}:
        return JsonResponse(
            {
                "error": "currency must be one of: "
                + ", ".join(item.value for item in Currency)
            },
            status=400,
        )

    use_case = GetProductListUseCase(
        products=ProductRepositoryImpl(),
        product_prices=ProductPriceRepositoryImpl(),
    )

    products = await sync_to_async(
        use_case.execute,
        thread_sensitive=True,
    )(
        GetProductListDTO(
            pagination=PaginationDTO(limit=limit, offset=offset),
            is_active=True,
            currency=currency,
        )
    )
    return JsonResponse(
        {"products": [_serialize_product(product) for product in products]}
    )
