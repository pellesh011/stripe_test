import pytest

from payments.domain.entities.tax import Tax
from payments.domain.exceptions import TaxNameError, TaxValueError


def test_tax_create():
    test_tax = Tax(name="VAT", rate=20)
    assert test_tax.name == "VAT"
    assert test_tax.rate == 20


def test_tax_create_wrong_name():
    with pytest.raises(TaxNameError):
        Tax(name=" ", rate=20)


def test_tax_create_wrong_rate_negative():
    with pytest.raises(TaxValueError):
        Tax(name="VAT", rate=-1)


def test_tax_create_wrong_rate_too_high():
    with pytest.raises(TaxValueError):
        Tax(name="VAT", rate=101)
