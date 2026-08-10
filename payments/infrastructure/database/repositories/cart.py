from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.cart import Cart
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.cart import CartRepository
from payments.infrastructure.database.models.cart import CartModel
from payments.infrastructure.database.repositories.loaders import build_cart


class CartRepositoryImpl(CartRepository):
    async def get_by_id(self, id: int) -> Cart:
        try:
            model = await CartModel.objects.select_related("currency").aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return await build_cart(model)

    async def save(self, cart: Cart) -> None:
        assert cart.currency.id is not None

        if cart.id is None:
            model = await CartModel.objects.acreate(
                currency_id=cart.currency.id,
                status=cart.status.value,
            )
            cart.id = model.id
        else:
            await CartModel.objects.filter(id=cart.id).aupdate(
                currency_id=cart.currency.id,
                status=cart.status.value,
            )
