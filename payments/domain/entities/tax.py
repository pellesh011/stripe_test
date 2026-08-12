from payments.domain.exceptions import TaxNameError, TaxValueError


class Tax:
    id: int | None
    name: str
    rate: int

    def __init__(
        self,
        name: str,
        rate: int,
        id: int | None = None,
    ):
        self.id = id
        if len(name.strip()) == 0:
            raise TaxNameError()
        self.name = name
        self.rate = rate
        if not 0 <= self.rate <= 100:
            raise TaxValueError()

    @classmethod
    def restore(
        cls,
        name: str,
        rate: int,
        id: int | None = None,
    ) -> Tax:
        return cls(name=name, rate=rate, id=id)
