from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentWebhookDTO:
    event_id: str
    event_type: str
    payment_intent_id: str
