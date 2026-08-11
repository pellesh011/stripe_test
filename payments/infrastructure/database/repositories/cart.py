from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.cart import Cart
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.cart import CartRepository
from payments.infrastructure.database.models.cart import CartModel
from payments.infrastructure.database.repositories.loaders import build_cart


class CartRepositoryImpl(CartRepository):
    async def get_by_id(self, id: int) -> Cart:
        try:
            model = await CartModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return await sync_to_async(build_cart)(model)

    async def save(self, cart: Cart) -> None:
        if cart.id is None:
            model = await CartModel.objects.acreate(
                status=cart.status.value,
            )
            cart.id = model.id
        else:
            await CartModel.objects.filter(id=cart.id).aupdate(
                status=cart.status.value,
            )
