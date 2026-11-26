
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Channel:
    channel_id: str
    name: str
    genre: str
    is_hd: bool
    is_fta: bool
    price: Decimal

    def __post_init__(self):
        self.price = Decimal(str(self.price))

        if self.price < 0:
            raise ValueError("Channel price cannot be negative")

        if self.is_fta and self.price != Decimal("0"):
            raise ValueError("FTA channels must have zero individual price")