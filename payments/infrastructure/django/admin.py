from django.contrib import admin

from payments.infrastructure.database.models.cart import (
    CartItemModel,
    CartModel,
)
from payments.infrastructure.database.models.discount import (
    DiscountModel,
)
from payments.infrastructure.database.models.exchange_rate import (
    ExchangeRateModel,
)
from payments.infrastructure.database.models.order import (
    OrderItemModel,
    OrderModel,
)
from payments.infrastructure.database.models.payment import (
    PaymentModel,
)
from payments.infrastructure.database.models.payment_attempt import (
    PaymentAttemptModel,
)
from payments.infrastructure.database.models.payment_provider import (
    PaymentProviderModel,
)
from payments.infrastructure.database.models.product import (
    ProductModel,
    ProductPriceModel,
)
from payments.infrastructure.database.models.stripe_webhook import (
    StripeWebhookEventModel,
)
from payments.infrastructure.database.models.tax import (
    TaxModel,
)


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(ProductPriceModel)
class ProductPriceModelAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "currency", "price", "is_active")
    list_filter = ("currency", "is_active")
    search_fields = ("product__name",)


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "created_at")
    list_filter = ("status", "created_at")


@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "product_price")
    list_filter = ("cart__status",)
    search_fields = ("product__name",)


@admin.register(DiscountModel)
class DiscountModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "value", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("name",)


@admin.register(ExchangeRateModel)
class ExchangeRateModelAdmin(admin.ModelAdmin):
    list_display = ("id", "base_currency", "currency", "coef", "is_active")
    list_filter = ("base_currency", "currency", "is_active")


@admin.register(TaxModel)
class TaxModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rate")
    search_fields = ("name",)


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "currency",
        "status",
        "discount",
        "tax",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")


@admin.register(OrderItemModel)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "product_price",
        "exchange_rate",
        "price",
    )
    search_fields = ("product__name",)


@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "user", "amount", "currency", "status")
    list_filter = ("status", "currency")
    search_fields = ("order__id",)


@admin.register(PaymentProviderModel)
class PaymentProviderModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(PaymentAttemptModel)
class PaymentAttemptModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment",
        "provider",
        "external_id",
        "status",
        "created_at",
        "completed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("external_id",)


@admin.register(StripeWebhookEventModel)
class StripeWebhookEventModelAdmin(admin.ModelAdmin):
    list_display = ("id", "event_id", "event_type", "status", "created_at")
    list_filter = ("event_type", "status", "created_at")
    search_fields = ("event_id", "event_type")
