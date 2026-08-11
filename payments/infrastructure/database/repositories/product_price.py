from django.core.exceptions import ObjectDoesNotExist

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
    async def get_by_id(self, id: int) -> ProductPrice:
        try:
            model = await ProductPriceModel.objects.select_related(
                "currency",
                "product",
            ).aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_price_to_entity(model)

    async def get_active(self, limit: int = 10, offset: int = 0) -> list[ProductPrice]:
        qs = (
            ProductPriceModel.objects.filter(is_active=True)
            .select_related("currency", "product")
            .order_by("id")[offset : offset + limit]
        )
        return [product_price_to_entity(model) async for model in qs]

    async def get_active_by_product_id(self, product_id: int) -> ProductPrice:
        try:
            model = (
                await ProductPriceModel.objects.filter(
                    product_id=product_id,
                    is_active=True,
                )
                .select_related("currency", "product")
                .aget()
            )
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_price_to_entity(model)

    async def save(self, product_price: ProductPrice) -> None:
        assert product_price.product.id is not None
        assert product_price.currency.id is not None

        if product_price.id is None:
            model = await ProductPriceModel.objects.acreate(
                product_id=product_price.product.id,
                currency_id=product_price.currency.id,
                price=product_price.price,
                is_active=product_price.is_active,
            )
            product_price.id = model.id
        else:
            await ProductPriceModel.objects.filter(id=product_price.id).aupdate(
                product_id=product_price.product.id,
                currency_id=product_price.currency.id,
                price=product_price.price,
                is_active=product_price.is_active,
            )
