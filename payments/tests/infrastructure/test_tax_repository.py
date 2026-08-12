import pytest

from payments.domain.entities.tax import Tax
from payments.domain.exceptions import EntityNotFoundError


@pytest.mark.django_db
def test_get_by_id(tax_repo, tax, call):
    assert tax.id is not None
    loaded = call(tax_repo.get_by_id)(tax.id)
    assert loaded.id == tax.id
    assert loaded.name == "VAT"
    assert loaded.rate == 20


@pytest.mark.django_db
def test_get_by_id_not_found(tax_repo, call):
    with pytest.raises(EntityNotFoundError):
        call(tax_repo.get_by_id)(9999)


@pytest.mark.django_db
def test_save_create_assigns_id(tax_repo, call):
    entity = Tax(name="Sales Tax", rate=10)
    assert entity.id is None

    call(tax_repo.save)(entity)

    assert entity.id is not None


@pytest.mark.django_db
def test_save_update(tax_repo, tax, call):
    assert tax.id is not None
    tax.name = "Renamed Tax"
    tax.rate = 21

    call(tax_repo.save)(tax)

    loaded = call(tax_repo.get_by_id)(tax.id)
    assert loaded.name == "Renamed Tax"
    assert loaded.rate == 21
