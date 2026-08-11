from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from payments.domain.exceptions import ProductNameError

if TYPE_CHECKING:
    from payments.domain.entities.product_price import ProductPrice


@dataclass
class Product:
    id: int | None
    name: str
    is_active: bool
    prices: list[ProductPrice] = field(default_factory=list)

    def __init__(self, name: str, is_active: bool, id: int | None = None):
        self.id = id
        if len(name.strip()) == 0:
            raise ProductNameError()
        self.name = name
        self.is_active = is_active
        self.prices = []

    def set_name(self, name: str):
        if len(name.strip()) == 0:
            raise ProductNameError()
        self.name = name
        return

    @classmethod
    def restore(
        cls,
        id: int,
        name: str,
        is_active: bool,
        prices: list[ProductPrice] | None = None,
    ) -> Product:
        product = cls(name, is_active, id)
        product.prices = prices or []
        return product
