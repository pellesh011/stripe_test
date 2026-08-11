from payments.application.dto.product import GetProductListDTO
from payments.domain.entities.product import Product
from payments.domain.repositories.product import ProductRepository
from payments.infrastructure.database.uow import DjangoUnitOfWork


class GetProductListUseCase:
    def __init__(
        self,
        products: ProductRepository,
        uow: DjangoUnitOfWork,
    ):
        self.uow = uow
        self.products = products

    async def execute(self, data: GetProductListDTO) -> list[Product]:
        products_list = await self.products.get_active(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
        )
        return products_list
