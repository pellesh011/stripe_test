from abc import ABC, abstractmethod

from payments.domain.entities.cart import Cart


class CartRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Cart: ...

    @abstractmethod
    async def save(self, cart: Cart) -> None: ...
