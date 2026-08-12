from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.cart_item import CartItem
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.cart_item import CartItemRepository
from payments.infrastructure.database.models.cart import CartItemModel
from payments.infrastructure.database.repositories.loaders import (
    CART_ITEM_SELECT_RELATED,
)
from payments.infrastructure.database.repositories.mappers import cart_item_to_entity


class CartItemRepositoryImpl(CartItemRepository):
    def get_by_id(self, id: int) -> CartItem:
        try:
            model = CartItemModel.objects.select_related(*CART_ITEM_SELECT_RELATED).get(
                id=id
            )
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return cart_item_to_entity(model)

    def get_by_cart_id(
        self, cart_id: int, limit: int = 10, offset: int = 0
    ) -> list[CartItem]:
        qs = (
            CartItemModel.objects.filter(cart_id=cart_id)
            .select_related(*CART_ITEM_SELECT_RELATED)
            .order_by("id")[offset : offset + limit]
        )
        return [cart_item_to_entity(model) for model in qs]

    def save(self, cart_item: CartItem) -> None:
        if cart_item.cart is None:
            raise ValueError("cart_item must reference a cart to be saved")

        assert cart_item.cart.id is not None
        assert cart_item.product.id is not None
        assert cart_item.product_price.id is not None

        if cart_item.id is None:
            model = CartItemModel.objects.create(
                cart_id=cart_item.cart.id,
                product_id=cart_item.product.id,
                product_price_id=cart_item.product_price.id,
            )
            cart_item.id = model.id
        else:
            CartItemModel.objects.filter(id=cart_item.id).update(
                cart_id=cart_item.cart.id,
                product_id=cart_item.product.id,
                product_price_id=cart_item.product_price.id,
            )
