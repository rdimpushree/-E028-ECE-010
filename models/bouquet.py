
from dataclasses import dataclass
from decimal import Decimal
from typing import List

@dataclass
class Bouquet:
    bouquet_id: str
    name: str
    channel_ids: List[str]
    price: Decimal

    def __post_init__(self):
        self.price = Decimal(str(self.price))

        if self.price < 0:
            raise ValueError("Bouquet price cannot be negative")

        if not self.channel_ids:
            raise ValueError("Bouquet must contain at least one channel")