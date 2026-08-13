from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutDTO:
    cart_id: int
    currency: str
    provider_id: int
    discount: str | None = None
    tax_id: int | None = None
