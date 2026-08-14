from payments.domain.entities.cart import Cart
from payments.domain.repositories.cart import CartRepository
from payments.domain.repositories.uow import UnitOfWork


class GetOrCreateActiveCartUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        carts: CartRepository,
    ):
        self.uow = uow
        self.carts = carts

    def execute(self) -> Cart:
        cart = self.carts.get_active_cart()
        if cart is not None:
            return cart

        cart = Cart()
        with self.uow:
            self.carts.save(cart)
        return cart
