from payments.application.dto.product import GetProductListDTO
from payments.domain.entities.exchange_rate import Currency
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

    def execute(self, data: GetProductListDTO) -> list[Product]:
        products_list = self.products.get_active(
            limit=data.pagination.limit,
            offset=data.pagination.offset,
        )
        product_ids = [
            product.id for product in products_list if product.id is not None
        ]
        currency = Currency(data.currency) if data.currency is not None else None
        prices = self.product_prices.get_active_by_product_ids(
            product_ids,
            currency=currency,
        )
        products_with_price = {price.product.id for price in prices}

        products_without_price = [
            product_id
            for product_id in product_ids
            if product_id not in products_with_price
        ]

        prices_other_currency = self.product_prices.get_active_by_product_ids(
            products_without_price,
        )
        prices.extend(prices_other_currency)
        prices_by_product_id: dict[int, list[ProductPrice]] = {}
        for price in prices:
            if price.product.id is not None:
                prices_by_product_id.setdefault(price.product.id, []).append(price)
        for product in products_list:
            if product.id is not None:
                product.prices = prices_by_product_id.get(product.id, [])
        return products_list
