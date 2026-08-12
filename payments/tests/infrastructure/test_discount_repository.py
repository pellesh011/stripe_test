from decimal import Decimal

import pytest

from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(discount_repo, discount, call):
    assert discount.id is not None
    loaded = call(discount_repo.get_by_id)(discount.id)
    assert loaded.id == discount.id
    assert loaded.name == "Test Discount"
    assert loaded.type == DiscountType.PERCENTAGE
    assert loaded.value == Decimal("10.00")
    assert loaded.is_active is True


@pytest.mark.django_db
def test_get_by_id_not_found(discount_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(discount_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_get_active(discount_repo, discount, inactive_discount, call):
    active = call(discount_repo.get_active)()
    active_ids = {item.id for item in active}

    assert discount.id in active_ids
    assert inactive_discount.id not in active_ids


@pytest.mark.django_db
def test_get_active_pagination_limit_and_offset(
    discount_repo, discount, inactive_discount, call
):
    for name in ("Discount 1", "Discount 2", "Discount 3"):
        entity = Discount(
            name=name,
            type=DiscountType.FIXED,
            value=Decimal("1.00"),
        )
        call(discount_repo.save)(entity)

    first_page = call(discount_repo.get_active)(limit=2, offset=0)
    second_page = call(discount_repo.get_active)(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_ids = {item.id for item in first_page}
    second_ids = {item.id for item in second_page}
    assert first_ids.isdisjoint(second_ids)
    assert discount.id in first_ids | second_ids
    assert inactive_discount.id not in first_ids | second_ids


@pytest.mark.django_db
def test_save_create_assigns_id(discount_repo, call):
    entity = Discount(
        name="New Discount",
        type=DiscountType.FIXED,
        value=Decimal("5.00"),
    )
    assert entity.id is None

    call(discount_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(discount_repo, discount, call):
    assert discount.id is not None
    discount.name = "Renamed Discount"
    discount.value = Decimal("15.00")
    discount.is_active = False

    call(discount_repo.save)(discount)

    loaded = call(discount_repo.get_by_id)(discount.id)
    assert loaded.name == "Renamed Discount"
    assert loaded.value == Decimal("15.00")
    assert loaded.is_active is False
