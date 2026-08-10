from dataclasses import dataclass

from payments.domain.exceptions import ProductNameError


@dataclass
class Product:

    id: int | None
    name: str
    is_active: bool

    def __init__(self, name: str, is_active: bool, id: int|None = None):
        self.id = id
        if len(name.strip()) == 0:
            raise ProductNameError()
        self.name = name
        self.is_active = is_active

    def set_name(self, name: str):
        if len(name.strip()) == 0:
            raise ProductNameError()
        self.name = name
        return 

    @classmethod
    def restore(cls, id: int, name: str, is_active: bool) -> Product:
        return cls(name, is_active, id)
        