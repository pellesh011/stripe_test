class ExchangeRateValueError(Exception):
    pass


class DiscountNameError(Exception):
    pass


class DiscountValueError(Exception):
    pass


class DiscountNotFoundError(Exception):
    pass


class DiscountNotActiveError(Exception):
    pass


class TaxNameError(Exception):
    pass


class TaxValueError(Exception):
    pass


class ProductNameError(Exception):
    pass


class ProductPriceNotActiveError(Exception):
    pass


class ProductNotActiveError(Exception):
    pass


class CartNotActiveError(Exception):
    pass


class CartEmptyError(Exception):
    pass


class CartItemNotFoundError(Exception):
    pass


class InvalidPaymentStatusTransition(Exception):
    pass


class PaymentCurrencyMismatchError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass


class IdentificatorError(Exception):
    pass


class PaymentClientSecretMissingError(Exception):
    pass
