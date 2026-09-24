import random
from datetime import datetime

from ticker.models import PriceData


class MockDataSource:
    """Stand-in for a future real Bitcoin price API client.

    Any real data source should expose the same get_price() -> PriceData
    interface so it can be swapped in without touching display code.
    """

    def __init__(self):
        self._base_price = 62345.78
        self._base_change_pct = 2.34

    def get_price(self) -> PriceData:
        price = self._base_price + random.uniform(-50, 50)
        change = self._base_change_pct + random.uniform(-0.3, 0.3)
        return PriceData(
            symbol="BTC",
            name="BITCOIN",
            price_usd=price,
            change_24h_pct=change,
            last_updated=datetime.now(),
        )
