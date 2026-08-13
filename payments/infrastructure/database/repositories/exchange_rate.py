from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.exchange_rate import Currency, ExchangeRate
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.exchange_rate import ExchangeRateRepository
from payments.infrastructure.database.models.exchange_rate import ExchangeRateModel
from payments.infrastructure.database.repositories.mappers import (
    exchange_rate_to_entity,
)


class ExchangeRateRepositoryImpl(ExchangeRateRepository):
    def get_by_id(self, id: int) -> ExchangeRate:
        try:
            model = ExchangeRateModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return exchange_rate_to_entity(model)

    def get_active(self, limit: int = 10, offset: int = 0) -> list[ExchangeRate]:
        qs = ExchangeRateModel.objects.filter(is_active=True).order_by("id")[
            offset : offset + limit
        ]
        return [exchange_rate_to_entity(model) for model in qs]

    def get_active_by_code(self, currency: Currency) -> ExchangeRate:
        try:
            model = ExchangeRateModel.objects.filter(
                is_active=True,
                currency=currency.value,
            ).get()
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return exchange_rate_to_entity(model)

    def save(self, exchange_rate: ExchangeRate) -> None:
        if exchange_rate.id is None:
            model = ExchangeRateModel.objects.create(
                base_currency=exchange_rate.base_currency.value,
                currency=exchange_rate.currency.value,
                coef=exchange_rate.coef,
                is_active=exchange_rate.is_active,
            )
            exchange_rate.set_id(model.id)
        else:
            ExchangeRateModel.objects.filter(id=exchange_rate.id).update(
                is_active=exchange_rate.is_active,
            )
