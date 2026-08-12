from payments.domain.entities.cart import Cart
from payments.domain.entities.cart_item import CartItem
from payments.domain.entities.order import Order
from payments.domain.entities.order_item import OrderItem
from payments.domain.entities.payment import Payment
from payments.infrastructure.database.models.cart import (
    CartItemModel,
    CartModel,
)
from payments.infrastructure.database.models.order import (
    OrderItemModel,
    OrderModel,
)
from payments.infrastructure.database.models.payment import PaymentModel
from payments.infrastructure.database.repositories.mappers import (
    cart_item_to_entity,
    cart_to_entity,
    order_item_to_entity,
    order_to_entity,
    payment_to_entity,
)

CART_ITEM_SELECT_RELATED = (
    "product",
    "product_price__product",
)

ORDER_ITEM_SELECT_RELATED = (*CART_ITEM_SELECT_RELATED, "exchange_rate")


def load_cart_items(cart_id: int) -> list[CartItem]:
    return [
        cart_item_to_entity(model)
        for model in CartItemModel.objects.filter(cart_id=cart_id).select_related(
            *CART_ITEM_SELECT_RELATED
        )
    ]


def load_order_items(order_id: int) -> list[OrderItem]:
    return [
        order_item_to_entity(model)
        for model in OrderItemModel.objects.filter(order_id=order_id).select_related(
            *ORDER_ITEM_SELECT_RELATED
        )
    ]


def build_cart(model: CartModel) -> Cart:
    items = load_cart_items(model.id)
    return cart_to_entity(model, items)


def build_order(model: OrderModel) -> Order:
    cart = build_cart(model.cart)
    items = load_order_items(model.id)
    return order_to_entity(model, cart, items)


def build_payment(model: PaymentModel) -> Payment:
    order = build_order(model.order)
    return payment_to_entity(model, order)
