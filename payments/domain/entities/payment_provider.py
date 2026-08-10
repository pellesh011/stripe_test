from dataclasses import dataclass


@dataclass
class PaymentProvider:
    id: int | None
    name: str
