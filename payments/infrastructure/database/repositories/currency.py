from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.currency import Currencies, Currency
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.currency import CurrencyRepository
from payments.infrastructure.database.models.currency import CurrencyModel
from payments.infrastructure.database.repositories.mappers import currency_to_entity


class CurrencyRepositoryImpl(CurrencyRepository):
    async def get_by_id(self, id: int) -> Currency:
        try:
            model = await CurrencyModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return currency_to_entity(model)

    async def get_active(self) -> list[Currency]:
        return [
            currency_to_entity(model)
            async for model in CurrencyModel.objects.filter(is_active=True)
        ]

    async def get_active_by_code(self, currency: Currencies) -> Currency:
        try:
            model = await CurrencyModel.objects.filter(
                is_active=True,
                currency=currency.value,
            ).aget()
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return currency_to_entity(model)

    async def save(self, currency: Currency) -> None:
        if currency.id is None:
            model = await CurrencyModel.objects.acreate(
                base_currency=currency.base_currency.value,
                currency=currency.currency.value,
                coef=currency.coef,
                is_active=currency.is_active,
            )
            currency.id = model.id
        else:
            await CurrencyModel.objects.filter(id=currency.id).aupdate(
                base_currency=currency.base_currency.value,
                currency=currency.currency.value,
                coef=currency.coef,
                is_active=currency.is_active,
            )
