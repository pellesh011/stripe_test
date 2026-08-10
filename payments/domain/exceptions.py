class CurrencyValueError(Exception):
    pass


class ProductCurrencyError(Exception):
    pass


class ProductNameError(Exception):
    pass

class ProductPriceNotActiveError(Exception):
    pass

class ProductNotActiveError(Exception):
    pass


class CartNotActiveError(Exception):
    pass

class CartItemNotFoundError(Exception):
    pass

class InvalidPaymentStatusTransition(Exception):
    pass