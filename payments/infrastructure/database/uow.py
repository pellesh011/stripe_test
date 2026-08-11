from django.db import transaction


class DjangoUnitOfWork:
    def __init__(
        self,
        products,
    ):
        self.products = products

    async def __aenter__(self):

        self.transaction = transaction.atomic()
        self.transaction.__enter__()

        return self

    async def __aexit__(
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
