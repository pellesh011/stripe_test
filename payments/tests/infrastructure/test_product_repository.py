import pytest

from payments.domain.entities.product import Product
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(product_repo, product):
    assert product.id is not None
    loaded = product_repo.get_by_id(product.id)
    assert loaded.id == product.id
    assert loaded.name == "Test Product"
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(product_repo):
    with pytest.raises(EntityNotFoundError):
        product_repo.get_by_id(9999)


@pytest.mark.django_db
def test_get_active(product_repo, product, inactive_product):
    active = product_repo.get_active()
    active_ids = {item.id for item in active}

    assert product.id in active_ids
    assert inactive_product.id not in active_ids


@pytest.mark.django_db
def test_get_active_pagination_limit_and_offset(product_repo, product):
    for name in ("Product 1", "Product 2", "Product 3"):
        entity = Product(name=name, is_active=True)
        product_repo.save(entity)

    first_page = product_repo.get_active(limit=2, offset=0)
    second_page = product_repo.get_active(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert product.id in first_ids | second_ids


@pytest.mark.django_db
def test_save_create_assigns_id(product_repo):
    entity = Product(name="New Product", is_active=True)
    assert entity.id is None

    product_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(product_repo, product):
    assert product.id is not None
    product.set_name("Renamed Product")
    product.is_active = False

    product_repo.save(product)

    loaded = product_repo.get_by_id(product.id)
    assert loaded.name == "Renamed Product"
    assert loaded.is_active is False
