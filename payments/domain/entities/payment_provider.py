from dataclasses import dataclass


@dataclass
class PaymentProvider:
    id: int
    name: str
