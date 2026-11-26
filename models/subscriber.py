
from dataclasses import dataclass, field
from typing import List

from models.connection import Connection


@dataclass
class Subscriber:
    subscriber_id: str
    name: str
    tenure_months: int
    connections: List[Connection] = field(default_factory=list)
    address_id: str = ""
    connection_no: int = 1

    def __post_init__(self):
        if self.tenure_months <= 0:
            raise ValueError("Subscription tenure must be positive")

        if not self.connections:
            raise ValueError("Subscriber must have at least one TV connection")

        if self.connection_no not in (1, 2):
            raise ValueError("Connection number must be 1 or 2")
