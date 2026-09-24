from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceData:
    """Common shape produced by any data source (mock or real API)."""

    symbol: str
    name: str
    price_usd: float
    change_24h_pct: float
    last_updated: datetime
    is_stale: bool = False
