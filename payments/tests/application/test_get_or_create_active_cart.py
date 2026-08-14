import pytest

from payments.application.use_cases.cart.get_or_create_active_cart import (
    GetOrCreateActiveCartUseCase,
)
from payments.domain.entities.cart import CartStatus
from payments.infrastructure.database.uow import DjangoUnitOfWork


def _build_use_case(cart_repo):
    return GetOrCreateActiveCartUseCase(
        uow=DjangoUnitOfWork(),
        carts=cart_repo,
    )


@pytest.mark.django_db
def test_execute_creates_cart_when_none_exists(cart_repo):
    use_case = _build_use_case(cart_repo)

    result = use_case.execute()

    assert result.id is not None
    assert result.status is CartStatus.ACTIVE

    loaded = cart_repo.get_by_id(result.id)
    assert loaded.id == result.id
    assert loaded.status is CartStatus.ACTIVE


@pytest.mark.django_db
def test_execute_returns_existing_active_cart(cart_repo, cart):
    use_case = _build_use_case(cart_repo)

    result = use_case.execute()

    assert result.id == cart.id
    assert result.status is CartStatus.ACTIVE


@pytest.mark.django_db
def test_execute_creates_new_cart_when_only_checkout_exists(cart_repo, cart):
    assert cart.id is not None
    cart.status = CartStatus.CHECKOUT
    cart_repo.save(cart)

    use_case = _build_use_case(cart_repo)

    result = use_case.execute()

    assert result.id is not None
    assert result.id != cart.id
    assert result.status is CartStatus.ACTIVE
