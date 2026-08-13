import pytest

from payments.tests.application.fakes import FakePaymentGateway
from payments.tests.infrastructure.conftest import *  # noqa: F403


@pytest.fixture
def payment_gateway() -> FakePaymentGateway:
    return FakePaymentGateway()
