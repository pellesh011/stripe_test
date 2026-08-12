from payments.application.dto.cart import AddToCartDTO
from payments.domain.entities.cart import Cart, CartStatus
from payments.domain.entities.cart_item import CartItem
from payments.domain.exceptions import (
    CartNotActiveError,
    EntityNotFoundError,
    ProductNotActiveError,
    ProductPriceNotActiveError,
)
from payments.domain.repositories.cart import CartRepository
from payments.domain.repositories.cart_item import CartItemRepository
from payments.domain.repositories.product import ProductRepository
from payments.domain.repositories.product_price import ProductPriceRepository


class AddToCartUseCase:
    def __init__(
        self,
        carts: CartRepository,
        cart_items: CartItemRepository,
        products: ProductRepository,
        product_prices: ProductPriceRepository,
    ):
        self.carts = carts
        self.cart_items = cart_items
        self.products = products
        self.product_prices = product_prices

    def execute(self, data: AddToCartDTO) -> CartItem:
        product = self.products.get_by_id(data.product_id)
        if not product.is_active:
            raise ProductNotActiveError()

        product_price = self.product_prices.get_by_id(data.product_price_id)
        if not product_price.is_active:
            raise ProductPriceNotActiveError()
        if product_price.product.id != product.id:
            raise EntityNotFoundError()

        if data.cart_id is not None:
            cart = self.carts.get_by_id(data.cart_id)
            if cart.status is not CartStatus.ACTIVE:
                raise CartNotActiveError()
        else:
            cart = Cart()

        cart_item = CartItem(
            product=product,
            product_price=product_price,
            cart=cart,
        )
        cart.add(cart_item)

        if cart.id is None:
            self.carts.save(cart)
        self.cart_items.save(cart_item)

        return cart_item
