from payments.application.dto.product import GetProductListDTO
from payments.domain.entities.exchange_rate import Currencies
from payments.domain.entities.product import Product
from payments.domain.entities.product_price import ProductPrice
from payments.domain.repositories.product import ProductRepository
from payments.domain.repositories.product_price import ProductPriceRepository


class GetProductListUseCase:
    def __init__(
        self,
        products: ProductRepository,
        product_prices: ProductPriceRepository,
    ):
        self.products = products
        self.product_prices = product_prices

    async def execute(self, data: GetProductListDTO) -> list[Product]:
        products_list = await self.products.get_active(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
        )
        product_ids = [
            product.id for product in products_list if product.id is not None
        ]
        currency = Currencies(data.currency) if data.currency is not None else None
        prices = await self.product_prices.get_active_by_product_ids(
            product_ids,
            currency=currency,
        )
        prices_by_product_id: dict[int, list[ProductPrice]] = {}
        for price in prices:
            if price.product.id is not None:
                prices_by_product_id.setdefault(price.product.id, []).append(price)
        for product in products_list:
            if product.id is not None:
                product.prices = prices_by_product_id.get(product.id, [])
        return products_list
