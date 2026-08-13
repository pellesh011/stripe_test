import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from payments.application.dto.checkout import CheckoutDTO
from payments.application.dto.product import GetProductListDTO, PaginationDTO
from payments.application.use_cases.order.checkout import CheckoutUseCase
from payments.application.use_cases.product.get_product_list import (
    GetProductListUseCase,
)
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order
from payments.domain.entities.payment import Payment
from payments.domain.entities.product import Product
from payments.domain.exceptions import (
    CartEmptyError,
    CartNotActiveError,
    DiscountNotActiveError,
    DiscountNotFoundError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)
from payments.infrastructure.database.repositories.cart import CartRepositoryImpl
from payments.infrastructure.database.repositories.discount import (
    DiscountRepositoryImpl,
)
from payments.infrastructure.database.repositories.exchange_rate import (
    ExchangeRateRepositoryImpl,
)
from payments.infrastructure.database.repositories.order import OrderRepositoryImpl
from payments.infrastructure.database.repositories.order_item import (
    OrderItemRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment import (
    PaymentRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment_attempt import (
    PaymentAttemptRepositoryImpl,
)
from payments.infrastructure.database.repositories.payment_provider import (
    PaymentProviderRepositoryImpl,
)
from payments.infrastructure.database.repositories.product import (
    ProductRepositoryImpl,
)
from payments.infrastructure.database.repositories.product_price import (
    ProductPriceRepositoryImpl,
)
from payments.infrastructure.database.repositories.tax import TaxRepositoryImpl
from payments.infrastructure.database.uow import DjangoUnitOfWork

_CHECKOUT_ERRORS: dict[type[Exception], tuple[int, str]] = {
    EntityNotFoundError: (404, "Entity not found"),
    DiscountNotFoundError: (404, "Discount not found"),
    CartEmptyError: (400, "Cart is empty"),
    CartNotActiveError: (400, "Cart is not active"),
    DiscountNotActiveError: (400, "Discount is not active"),
    ProductNotActiveError: (400, "Product is not active"),
    ProductPriceNotActiveError: (400, "Product price is not active"),
}


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


def get_product_list(request) -> JsonResponse:
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
    products = use_case.execute(
        GetProductListDTO(
            pagination=PaginationDTO(limit=limit, offset=offset),
            is_active=True,
            currency=currency,
        )
    )
    return JsonResponse(
        {"products": [_serialize_product(product) for product in products]}
    )


def _parse_required_id(data, field: str) -> tuple[int | None, str | None]:
    raw = data.get(field)
    if raw is None:
        return None, f"{field} is required"
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw, None
    return None, f"{field} must be an integer"


def _parse_optional_int(data, field: str) -> tuple[int | None, str | None]:
    raw = data.get(field)
    if raw is None:
        return None, None
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw, None
    return None, f"{field} must be an integer"


def _serialize_order_item(item) -> dict:
    return {
        "id": item.id,
        "product_id": item.product.id,
        "product_name": item.product.name,
        "price": str(item.price),
        "currency": item.exchange_rate.currency.value,
    }


def _serialize_order(order: Order, payment: Payment) -> dict:
    return {
        "id": order.id,
        "currency": order.currency.value,
        "status": order.status.value,
        "subtotal": str(order.subtotal()),
        "tax_amount": str(order.tax_amount()),
        "discount_amount": str(order.discount_amount()),
        "total": str(order.total()),
        "tax": (
            {
                "id": order.tax.id,
                "name": order.tax.name,
                "rate": order.tax.rate,
            }
            if order.tax is not None
            else None
        ),
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
        "items": [_serialize_order_item(item) for item in order.items],
        "payment": {
            "id": payment.id,
            "amount": str(payment.amount),
            "currency": payment.currency.value,
            "status": payment.status.value,
        },
    }


@csrf_exempt
def checkout(request) -> JsonResponse:
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

    cart_id, error = _parse_required_id(data, "cart_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)
    assert cart_id is not None

    provider_id, error = _parse_required_id(data, "provider_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)
    assert provider_id is not None

    tax_id, error = _parse_optional_int(data, "tax_id")
    if error is not None:
        return JsonResponse({"error": error}, status=400)

    currency = data.get("currency")
    if currency not in {item.value for item in Currency}:
        return JsonResponse(
            {
                "error": "currency must be one of: "
                + ", ".join(item.value for item in Currency)
            },
            status=400,
        )

    discount = data.get("discount")
    if discount is not None and not isinstance(discount, str):
        return JsonResponse(
            {"error": "discount must be a string"},
            status=400,
        )
    if isinstance(discount, str) and discount.strip() == "":
        discount = None

    use_case = CheckoutUseCase(
        uow=DjangoUnitOfWork(),
        carts=CartRepositoryImpl(),
        orders=OrderRepositoryImpl(),
        order_items=OrderItemRepositoryImpl(),
        exchange_rates=ExchangeRateRepositoryImpl(),
        discounts=DiscountRepositoryImpl(),
        taxes=TaxRepositoryImpl(),
        payments=PaymentRepositoryImpl(),
        payment_attempts=PaymentAttemptRepositoryImpl(),
        payment_providers=PaymentProviderRepositoryImpl(),
    )

    try:
        order = use_case.execute(
            CheckoutDTO(
                cart_id=cart_id,
                currency=currency,
                provider_id=provider_id,
                discount=discount,
                tax_id=tax_id,
            )
        )
    except tuple(_CHECKOUT_ERRORS) as exc:
        status, message = _CHECKOUT_ERRORS[type(exc)]
        return JsonResponse({"error": message}, status=status)

    assert order.id is not None
    payment = PaymentRepositoryImpl().get_by_order_id(order.id)
    return JsonResponse(_serialize_order(order, payment))
