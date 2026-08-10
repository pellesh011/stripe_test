from abc import ABC, abstractmethod

from payments.domain.entities.cart_item import CartItem


class CartItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> CartItem: ...

    @abstractmethod
    async def get_by_cart_id(self, cart_id: int) -> list[CartItem]: ...

    @abstractmethod
    async def save(self, cart_item: CartItem) -> None: ...
