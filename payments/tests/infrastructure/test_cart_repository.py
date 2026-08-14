import pytest

from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id_not_found(cart_repo):
    with pytest.raises(EntityNotFoundError):
        cart_repo.get_by_id(9999)


@pytest.mark.django_db
def test_get_by_id_for_update(cart_repo, cart):
    assert cart.id is not None
    loaded = cart_repo.get_by_id_for_update(cart.id)

    assert loaded.id == cart.id
    assert loaded.status is CartStatus.ACTIVE


@pytest.mark.django_db
def test_get_by_id_for_update_not_found(cart_repo):
    with pytest.raises(EntityNotFoundError):
        cart_repo.get_by_id_for_update(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(cart_repo):
    entity = Cart()
    assert entity.id is None

    cart_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_get_by_id_returns_cart(cart_repo, cart):
    assert cart.id is not None
    loaded = cart_repo.get_by_id(cart.id)

    assert loaded.id == cart.id
    assert loaded.items == []
    assert loaded.status is CartStatus.ACTIVE


@pytest.mark.django_db
def test_save_update_status(cart_repo, cart):
    assert cart.id is not None
    cart.status = CartStatus.CHECKOUT

    cart_repo.save(cart)

    loaded = cart_repo.get_by_id(cart.id)
    assert loaded.status is CartStatus.CHECKOUT


@pytest.mark.django_db
def test_get_by_id_loads_items(cart_repo, cart, cart_item):
    assert cart.id is not None
    loaded = cart_repo.get_by_id(cart.id)

    assert len(loaded.items) == 1
    assert loaded.items[0].id == cart_item.id
    assert loaded.items[0].product.name == cart_item.product.name


@pytest.mark.django_db
def test_get_active_cart_returns_none_when_no_active(cart_repo):
    assert cart_repo.get_active_cart() is None


@pytest.mark.django_db
def test_get_active_cart_returns_latest_active(cart_repo):
    first = Cart()
    cart_repo.save(first)
    second = Cart()
    cart_repo.save(second)

    assert first.id is not None
    assert second.id is not None
    second.status = CartStatus.CHECKOUT
    cart_repo.save(second)

    third = Cart()
    cart_repo.save(third)

    loaded = cart_repo.get_active_cart()

    assert loaded is not None
    assert loaded.id == third.id
    assert loaded.status is CartStatus.ACTIVE
