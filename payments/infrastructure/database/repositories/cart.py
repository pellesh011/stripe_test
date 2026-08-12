from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.cart import Cart
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.cart import CartRepository
from payments.infrastructure.database.models.cart import CartModel
from payments.infrastructure.database.repositories.loaders import build_cart


class CartRepositoryImpl(CartRepository):
    def get_by_id(self, id: int) -> Cart:
        try:
            model = CartModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return build_cart(model)

    def save(self, cart: Cart) -> None:
        if cart.id is None:
            model = CartModel.objects.create(
                status=cart.status.value,
            )
            cart.id = model.id
        else:
            CartModel.objects.filter(id=cart.id).update(
                status=cart.status.value,
            )