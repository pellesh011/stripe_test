from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.product import Product
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.product import ProductRepository
from payments.infrastructure.database.models.product import ProductModel
from payments.infrastructure.database.repositories.mappers import product_to_entity


class ProductRepositoryImpl(ProductRepository):
    async def get_by_id(self, id: int) -> Product:
        try:
            model = await ProductModel.objects.aget(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_to_entity(model)

    async def get_active(self, limit: int = 10, offset: int = 0) -> list[Product]:
        qs = ProductModel.objects.filter(is_active=True).order_by("id")[
            offset : offset + limit
        ]
        return [product_to_entity(model) async for model in qs]

    async def save(self, product: Product) -> None:
        if product.id is None:
            model = await ProductModel.objects.acreate(
                name=product.name,
                is_active=product.is_active,
            )
            product.id = model.id
        else:
            await ProductModel.objects.filter(id=product.id).aupdate(
                name=product.name,
                is_active=product.is_active,
            )
