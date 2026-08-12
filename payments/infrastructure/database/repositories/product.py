from django.core.exceptions import ObjectDoesNotExist

from payments.domain.entities.product import Product
from payments.domain.exceptions import EntityNotFoundError
from payments.domain.repositories.product import ProductRepository
from payments.infrastructure.database.models.product import ProductModel
from payments.infrastructure.database.repositories.mappers import product_to_entity


class ProductRepositoryImpl(ProductRepository):
    def get_by_id(self, id: int) -> Product:
        try:
            model = ProductModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise EntityNotFoundError() from None
        return product_to_entity(model)

    def get_active(self, limit: int = 10, offset: int = 0) -> list[Product]:
        qs = ProductModel.objects.filter(is_active=True).order_by("id")[
            offset : offset + limit
        ]
        return [product_to_entity(model) for model in qs]

    def save(self, product: Product) -> None:
        if product.id is None:
            model = ProductModel.objects.create(
                name=product.name,
                is_active=product.is_active,
            )
            product.id = model.id
        else:
            ProductModel.objects.filter(id=product.id).update(
                name=product.name,
                is_active=product.is_active,
            )
