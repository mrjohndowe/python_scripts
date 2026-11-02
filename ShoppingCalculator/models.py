from dataclasses import dataclass, asdict
from decimal import Decimal


@dataclass
class ShoppingItem:
    name: str
    price: Decimal
    quantity: int = 1
    taxable: bool = True

    @property
    def total(self):
        return self.price * self.quantity

    def to_dict(self):
        d = asdict(self)
        d["price"] = str(self.price)
        return d

    @staticmethod
    def from_dict(data):
        return ShoppingItem(
            name=data["name"],
            price=Decimal(data["price"]),
            quantity=data.get("quantity", 1),
            taxable=data.get("taxable", True),
        )
