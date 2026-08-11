from dataclasses import dataclass


@dataclass(frozen=True)
class PaginationDTO:
    limit: int = 10
    offset: int = 0


@dataclass(frozen=True)
class GetProductListDTO:
    pagination: PaginationDTO
    is_active: bool | None
    currency: str | None
