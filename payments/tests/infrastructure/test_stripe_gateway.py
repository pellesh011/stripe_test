from decimal import Decimal
from unittest.mock import patch

import pytest
import stripe

from payments.domain.entities.cart import Cart
from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.order import Order
from payments.domain.entities.tax import Tax
from payments.domain.exceptions import PaymentClientSecretMissingError
from payments.domain.services.payment_gateway import PaymentGateway, PaymentResult
from payments.infrastructure.stripe.gateway import StripePaymentGateway

API_KEY = "sk_test_123"


def build_order(
    *,
    discount: Discount | None = None,
    tax: Tax | None = None,
) -> Order:
    return Order(
        id=42,
        currency=Currency.EUR,
        cart=Cart(id=1),
        discount=discount,
        tax=tax,
    )


def mock_intent(mock_create):
    mock_create.return_value.id = "pi_test_123"
    mock_create.return_value.client_secret = "cs_test_secret"
    mock_create.return_value.status = "requires_payment_method"


def test_init_sets_stripe_api_key():
    StripePaymentGateway(api_key=API_KEY)

    assert stripe.api_key == API_KEY


def test_implements_payment_gateway():
    assert issubclass(StripePaymentGateway, PaymentGateway)


@patch("stripe.PaymentIntent.create")
def test_create_payment_passes_amount_currency_and_metadata(mock_create):
    discount = Discount(
        id=5,
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )
    tax = Tax(id=7, name="VAT", rate=20)
    order = build_order(discount=discount, tax=tax)
    gateway = StripePaymentGateway(api_key=API_KEY)
    mock_intent(mock_create)

    result = gateway.create_payment(
        order=order,
        amount=Decimal("10.50"),
        currency=Currency.EUR,
    )

    mock_create.assert_called_once_with(
        amount=1050,
        currency="eur",
        metadata={
            "order_id": "42",
            "discount_id": "5",
            "tax_id": "7",
        },
    )
    assert result == PaymentResult(
        id="pi_test_123",
        client_secret="cs_test_secret",
        status="requires_payment_method",
    )


@patch("stripe.PaymentIntent.create")
def test_create_payment_omits_missing_discount_and_tax(mock_create):
    order = build_order()
    gateway = StripePaymentGateway(api_key=API_KEY)
    mock_intent(mock_create)

    gateway.create_payment(
        order=order,
        amount=Decimal("10.00"),
        currency=Currency.USD,
    )

    mock_create.assert_called_once_with(
        amount=1000,
        currency="usd",
        metadata={"order_id": "42"},
    )


@patch("stripe.PaymentIntent.create")
def test_create_payment_raises_when_client_secret_missing(mock_create):
    mock_create.return_value.id = "pi_test_123"
    mock_create.return_value.client_secret = None
    mock_create.return_value.status = "requires_payment_method"
    gateway = StripePaymentGateway(api_key=API_KEY)

    with pytest.raises(PaymentClientSecretMissingError):
        gateway.create_payment(
            order=build_order(),
            amount=Decimal("10.00"),
            currency=Currency.EUR,
        )