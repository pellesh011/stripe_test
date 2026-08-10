from decimal import Decimal
from enum import Enum

from payments.domain.exceptions import DiscountNameError, DiscountValueError


class DiscountType(Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Discount:
    id: int | None
    name: str
    type: DiscountType
    value: Decimal
    is_active: bool

    def __init__(
        self,
        name: str,
        type: DiscountType,
        value: Decimal,
        is_active: bool = True,
        id: int | None = None,
    ):
        self.id = id
        if len(name.strip()) == 0:
            raise DiscountNameError()
        self.name = name
        self.type = type
        self.value = value
        self.is_active = is_active
        if self.value < 0:
            raise DiscountValueError()

    @classmethod
    def restore(
        cls,
        name: str,
        type: DiscountType,
        value: Decimal,
        is_active: bool,
        id: int | None = None,
    ) -> Discount:
        return cls(name=name, type=type, value=value, is_active=is_active, id=id)
