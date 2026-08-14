from dataclasses import dataclass

from payments.domain.entities.order import Order


@dataclass(frozen=True)
class PaginationDTO:
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True)
class OrdersPage:
    orders: list[Order]
    total: int
