from django.db import transaction

from payments.domain.repositories.uow import UnitOfWork


class DjangoUnitOfWork(UnitOfWork):
    def __init__(
        self,
        orders,
        order_items,
        payments,
        payment_attempts,
    ):
        self.orders = orders
        self.order_items = order_items
        self.payments = payments
        self.payment_attempts = payment_attempts

    def __enter__(self):
        self.transaction = transaction.atomic()
        self.transaction.__enter__()
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        self.transaction.__exit__(
            exc_type,
            exc,
            traceback,
        )
