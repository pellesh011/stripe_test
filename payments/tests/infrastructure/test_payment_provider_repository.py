import pytest

from payments.domain.entities.payment_provider import PaymentProvider
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(payment_provider_repo):
    with pytest.raises(EntityNotFoundError):
        payment_provider_repo.get_by_id(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(payment_provider_repo):
    entity = PaymentProvider(id=None, name="new-provider")
    assert entity.id is None

    payment_provider_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id(payment_provider_repo, payment_provider):
    assert payment_provider.id is not None
    loaded = payment_provider_repo.get_by_id(payment_provider.id)

    assert loaded.id == payment_provider.id
    assert loaded.name == "test-provider"


@pytest.mark.django_db
def test_save_update(payment_provider_repo, payment_provider):
    assert payment_provider.id is not None
    payment_provider.name = "renamed-provider"

    payment_provider_repo.save(payment_provider)

    loaded = payment_provider_repo.get_by_id(payment_provider.id)
    assert loaded.name == "renamed-provider"


@pytest.mark.django_db
def test_get_default_not_found(payment_provider_repo):
    with pytest.raises(EntityNotFoundError):
        payment_provider_repo.get_default()


@pytest.mark.django_db
def test_get_default_returns_first_provider(payment_provider_repo):
    first = PaymentProvider(id=None, name="first-provider")
    payment_provider_repo.save(first)
    second = PaymentProvider(id=None, name="second-provider")
    payment_provider_repo.save(second)

    assert first.id is not None
    loaded = payment_provider_repo.get_default()

    assert loaded.id == first.id
    assert loaded.name == "first-provider"
