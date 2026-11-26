
from dataclasses import dataclass, field
from typing import List

@dataclass
class Connection:
    connection_id: str
    channel_ids: List[str] = field(default_factory=list)
    bouquet_ids: List[str] = field(default_factory=list)