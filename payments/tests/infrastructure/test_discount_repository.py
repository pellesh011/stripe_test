from decimal import Decimal

import pytest

from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.exceptions import (
    DiscountNotActiveError,
    DiscountNotFoundError,
    EntityNotFoundError,
)


@pytest.mark.django_db
def test_get_by_id(discount_repo, discount):
    assert discount.id is not None
    loaded = discount_repo.get_by_id(discount.id)
    assert loaded.id == discount.id
    assert loaded.name == "Test Discount"
    assert loaded.type == DiscountType.PERCENTAGE
    assert loaded.value == Decimal("10.00")
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(discount_repo):
    with pytest.raises(EntityNotFoundError):
        discount_repo.get_by_id(9999)


@pytest.mark.django_db
def test_get_active(discount_repo, discount, inactive_discount):
    active = discount_repo.get_active()
    active_ids = {item.id for item in active}

    assert discount.id in active_ids
    assert inactive_discount.id not in active_ids


@pytest.mark.django_db
def test_get_active_by_name(discount_repo, discount):
    loaded = discount_repo.get_active_by_name(discount.name)

    assert loaded.id == discount.id
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_active_by_name_not_found(discount_repo):
    with pytest.raises(DiscountNotFoundError):
        discount_repo.get_active_by_name("missing")


@pytest.mark.django_db
def test_get_active_by_name_inactive(discount_repo, inactive_discount):
    with pytest.raises(DiscountNotActiveError):
        discount_repo.get_active_by_name(inactive_discount.name)


@pytest.mark.django_db
def test_get_active_pagination_limit_and_offset(
    discount_repo, discount, inactive_discount
):
    for name in ("Discount 1", "Discount 2", "Discount 3"):
        entity = Discount(
            name=name,
            type=DiscountType.FIXED,
            value=Decimal("1.00"),
        )
        discount_repo.save(entity)

    first_page = discount_repo.get_active(limit=2, offset=0)
    second_page = discount_repo.get_active(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert discount.id in first_ids | second_ids
    assert inactive_discount.id not in first_ids | second_ids


@pytest.mark.django_db
def test_save_create_assigns_id(discount_repo):
    entity = Discount(
        name="New Discount",
        type=DiscountType.FIXED,
        value=Decimal("5.00"),
    )
    assert entity.id is None

    discount_repo.save(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(discount_repo, discount):
    assert discount.id is not None
    discount.name = "Renamed Discount"
    discount.value = Decimal("15.00")
    discount.is_active = False

    discount_repo.save(discount)

    loaded = discount_repo.get_by_id(discount.id)
    assert loaded.name == "Renamed Discount"
    assert loaded.value == Decimal("15.00")
    assert loaded.is_active is False
