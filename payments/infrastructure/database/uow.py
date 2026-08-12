from django.db import transaction

from payments.domain.repositories.uow import UnitOfWork


class DjangoUnitOfWork(UnitOfWork):

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
