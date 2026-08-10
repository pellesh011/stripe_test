from payments.domain.entities.payment_provider import PaymentProvider


def test_payment_provider_create():
    test_provider = PaymentProvider(id=1, name="test-provider")

    assert test_provider.id == 1
    assert test_provider.name == "test-provider"


def test_payment_provider_create_without_id():
    test_provider = PaymentProvider(id=None, name="test-provider")

    assert test_provider.id is None
    assert test_provider.name == "test-provider"
