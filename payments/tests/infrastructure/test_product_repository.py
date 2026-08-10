import pytest

from payments.domain.entities.product import Product
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(product_repo, product, call):
    assert product.id is not None
    loaded = call(product_repo.get_by_id)(product.id)
    assert loaded.id == product.id
    assert loaded.name == "Test Product"
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(product_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(product_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_get_active(product_repo, product, inactive_product, call):
    active = call(product_repo.get_active)()
    active_ids = {item.id for item in active}

    assert product.id in active_ids
    assert inactive_product.id not in active_ids


@pytest.mark.django_db
def test_save_create_assigns_id(product_repo, call):
    entity = Product(name="New Product", is_active=True)
    assert entity.id is None

    call(product_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(product_repo, product, call):
    assert product.id is not None
    product.set_name("Renamed Product")
    product.is_active = False

    call(product_repo.save)(product)

    loaded = call(product_repo.get_by_id)(product.id)
    assert loaded.name == "Renamed Product"
    assert loaded.is_active is False
