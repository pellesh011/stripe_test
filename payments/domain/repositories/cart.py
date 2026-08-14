from abc import ABC, abstractmethod

from payments.domain.entities.cart import Cart


class CartRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Cart: ...

    @abstractmethod
    def get_by_id_for_update(self, id: int) -> Cart: ...

    @abstractmethod
    def get_active_cart(self) -> Cart | None: ...

    @abstractmethod
    def save(self, cart: Cart) -> None: ...
