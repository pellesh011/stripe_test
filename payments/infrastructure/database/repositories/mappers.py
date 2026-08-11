from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.exchange_rate import Currencies, ExchangeRate
from payments.domain.entities.order import Order, OrderStatus
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.payment import Payment, PaymentStatus
from payments.domain.entities.payment_attempts import (
    PaymentAttempt,
    PaymentAttemptStatus,
)
from payments.domain.entities.payment_provider import PaymentProvider
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.infrastructure.database.models.cart import CartItemModel, CartModel
from payments.infrastructure.database.models.discount import DiscountModel
from payments.infrastructure.database.models.exchange_rate import ExchangeRateModel
from payments.infrastructure.database.models.order import OrderItemModel, OrderModel
from payments.infrastructure.database.models.payment import PaymentModel
from payments.infrastructure.database.models.payment_attempt import (
    PaymentAttemptModel,
)
from payments.infrastructure.database.models.payment_provider import (
    PaymentProviderModel,
)
from payments.infrastructure.database.models.product import (
    ProductModel,
    ProductPriceModel,
)


def exchange_rate_to_entity(model: ExchangeRateModel) -> ExchangeRate:
    return ExchangeRate.restore(
        currency=Currencies(model.currency),
        coef=model.coef,
        is_active=model.is_active,
        id=model.id,
    )


def discount_to_entity(model: DiscountModel) -> Discount:
    return Discount.restore(
        name=model.name,
        type=DiscountType(model.type),
        value=model.value,
        is_active=model.is_active,
        id=model.id,
    )


def product_to_entity(model: ProductModel) -> Product:
    return Product.restore(
        id=model.id,
        name=model.name,
        is_active=model.is_active,
    )


def product_price_to_entity(model: ProductPriceModel) -> ProductPrice:
    return ProductPrice.restore(
        currency=Currencies(model.currency),
        price=model.price,
        product=product_to_entity(model.product),
        is_active=model.is_active,
        id=model.id,
    )


def cart_item_to_entity(model: CartItemModel) -> CartItem:
    return CartItem.restore(
        id=model.id,
        product=product_to_entity(model.product),
        product_price=product_price_to_entity(model.product_price),
    )


def order_item_to_entity(model: OrderItemModel) -> OrderItem:
    return OrderItem.restore(
        id=model.id,
        product=product_to_entity(model.product),
        product_price=product_price_to_entity(model.product_price),
    )


def cart_to_entity(model: CartModel, items: list[CartItem]) -> Cart:
    return Cart.restore(
        items=items,
        status=CartStatus(model.status),
        id=model.id,
    )


def order_to_entity(
    model: OrderModel,
    cart: Cart,
    items: list[OrderItem],
) -> Order:
    discount = (
        discount_to_entity(model.discount) if model.discount is not None else None
    )
    return Order.restore(
        currency=Currencies(model.currency),
        cart=cart,
        items=items,
        status=OrderStatus(model.status),
        discount=discount,
        id=model.id,
    )


def payment_provider_to_entity(model: PaymentProviderModel) -> PaymentProvider:
    return PaymentProvider(id=model.id, name=model.name)


def payment_to_entity(model: PaymentModel, order: Order) -> Payment:
    return Payment.restore(
        id=model.id,
        order=order,
        amount=model.amount,
        currency=exchange_rate_to_entity(model.currency),
        status=PaymentStatus(model.status),
    )


def payment_attempt_to_entity(
    model: PaymentAttemptModel,
    provider: PaymentProvider,
    payment: Payment,
) -> PaymentAttempt:
    return PaymentAttempt.restore(
        id=model.id,
        external_id=model.external_id,
        provider=provider,
        payment=payment,
        status=PaymentAttemptStatus(model.status),
        created_at=model.created_at,
        completed_at=model.completed_at,
    )
