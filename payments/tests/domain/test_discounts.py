from decimal import Decimal

import pytest

from payments.domain.entities.discount import Discount, DiscountType
from payments.domain.exceptions import DiscountNameError, DiscountValueError


def test_discount_create():
    test_discount = Discount(
        name="Test Discount",
        type=DiscountType.PERCENTAGE,
        value=Decimal("10.00"),
    )
    assert test_discount.name == "Test Discount"
    assert test_discount.type == DiscountType.PERCENTAGE
    assert test_discount.value == Decimal("10.00")
    assert test_discount.is_active is True


def test_discount_create_wrong_name():
    with pytest.raises(DiscountNameError):
        Discount(name=" ", type=DiscountType.FIXED, value=Decimal("5.00"))


def test_discount_create_wrong_value():
    with pytest.raises(DiscountValueError):
        Discount(name="Test Discount", type=DiscountType.FIXED, value=Decimal("-5.00"))
