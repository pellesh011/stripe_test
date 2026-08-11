from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.exchange_rate import Currencies, ExchangeRate
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.exchange_rate import ExchangeRateRepository
from payments.infrastructure.database.models.exchange_rate import ExchangeRateModel
from payments.infrastructure.database.repositories.mappers import (
    exchange_rate_to_entity,
)


class ExchangeRateRepositoryImpl(ExchangeRateRepository):
    async def get_by_id(self, id: int) -> ExchangeRate:
        try:
            model = await ExchangeRateModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return exchange_rate_to_entity(model)

    async def get_active(self, limit: int = 10, offset: int = 0) -> list[ExchangeRate]:
        qs = ExchangeRateModel.objects.filter(is_active=True).order_by("id")[
            offset : offset + limit
        ]
        return [exchange_rate_to_entity(model) async for model in qs]

    async def get_active_by_code(self, currency: Currencies) -> ExchangeRate:
        try:
            model = await ExchangeRateModel.objects.filter(
                is_active=True,
                currency=currency.value,
            ).aget()
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return exchange_rate_to_entity(model)

    async def save(self, exchange_rate: ExchangeRate) -> None:
        if exchange_rate.id is None:
            model = await ExchangeRateModel.objects.acreate(
                base_currency=exchange_rate.base_currency.value,
                currency=exchange_rate.currency.value,
                coef=exchange_rate.coef,
                is_active=exchange_rate.is_active,
            )
            exchange_rate.id = model.id
        else:
            await ExchangeRateModel.objects.filter(id=exchange_rate.id).aupdate(
                base_currency=exchange_rate.base_currency.value,
                currency=exchange_rate.currency.value,
                coef=exchange_rate.coef,
                is_active=exchange_rate.is_active,
            )
