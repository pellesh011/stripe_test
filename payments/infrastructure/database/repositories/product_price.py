from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.exchange_rate import Currency
from payments.domain.entities.product_price import ProductPrice
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.product_price import ProductPriceRepository
from payments.infrastructure.database.models.product import (
    ProductPriceModel,
)
from payments.infrastructure.database.repositories.mappers import (
    product_price_to_entity,
)


class ProductPriceRepositoryImpl(ProductPriceRepository):
    def get_by_id(self, id: int) -> ProductPrice:
        try:
            model = ProductPriceModel.objects.select_related(
                "product",
            ).get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_price_to_entity(model)

    def get_active(self, limit: int = 10, offset: int = 0) -> list[ProductPrice]:
        qs = (
            ProductPriceModel.objects.filter(is_active=True)
            .select_related("product")
            .order_by("id")[offset : offset + limit]
        )
        return [product_price_to_entity(model) for model in qs]

    def get_active_by_product_id(self, product_id: int) -> ProductPrice:
        try:
            model = (
                ProductPriceModel.objects.filter(
                    product_id=product_id,
                    is_active=True,
                )
                .select_related("product")
                .get()
            )
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_price_to_entity(model)

    def get_active_by_product_ids(
        self,
        product_ids: list[int],
        currency: Currency | None = None,
    ) -> list[ProductPrice]:
        qs = ProductPriceModel.objects.filter(
            product_id__in=product_ids,
            is_active=True,
        ).select_related("product")
        if currency is not None:
            qs = qs.filter(currency=currency.value)
        return [product_price_to_entity(model) for model in qs]

    def save(self, product_price: ProductPrice) -> None:
        assert product_price.product.id is not None

        if product_price.id is None:
            model = ProductPriceModel.objects.create(
                product_id=product_price.product.id,
                currency=product_price.currency.value,
                price=product_price.price,
                is_active=product_price.is_active,
            )
            product_price.set_id(model.id)
        else:
            ProductPriceModel.objects.filter(id=product_price.id).update(
                is_active=product_price.is_active,
            )
