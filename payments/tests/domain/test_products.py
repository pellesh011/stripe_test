import pytest

from payments.domain.entities.product import Product
from payments.domain.exceptions import ProductNameError


def test_product_create():
    test_product = Product("test name", True)
    assert test_product.name == "test name"


def test_product_create_wrong_name():
    with pytest.raises(ProductNameError):
        Product(" ", True)
