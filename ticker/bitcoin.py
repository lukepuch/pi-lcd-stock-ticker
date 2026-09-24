"""Live BTC/USD price retrieval. Kept separate from the mock data source
and from all Tkinter/display code so it can be unit-tested on its own.
"""

import json
import time
from dataclasses import replace
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from ticker.models import PriceData

API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
)
DEFAULT_TIMEOUT = 5  # seconds
DEFAULT_MIN_INTERVAL = 60  # seconds; don't hit the API more often than this


class PriceFetchError(Exception):
    """Raised when the BTC price can't be retrieved or parsed."""


def fetch_btc_price(timeout: float = DEFAULT_TIMEOUT) -> PriceData:
    """Hit the CoinGecko API once and return the current BTC/USD price.

    Raises PriceFetchError on any network, HTTP, or parsing failure.
    """
    request = Request(API_URL, headers={"User-Agent": "pi-lcd-stock-ticker/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        data = payload["bitcoin"]
        return PriceData(
            symbol="BTC",
            name="BITCOIN",
            price_usd=float(data["usd"]),
            change_24h_pct=float(data["usd_24h_change"]),
            last_updated=datetime.now(),
        )
    except (URLError, TimeoutError, ValueError, KeyError) as exc:
        raise PriceFetchError(f"failed to fetch BTC price: {exc}") from exc


class BitcoinDataSource:
    """get_price()-compatible live data source (same interface as MockDataSource).

    Never calls the API more than once per `min_interval` seconds. If a
    fetch fails, returns the last successful price marked stale instead of
    raising, so the display never crashes over a bad connection. Only
    raises if no price has ever been fetched successfully yet.
    """

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        min_interval: float = DEFAULT_MIN_INTERVAL,
    ):
        self.timeout = timeout
        self.min_interval = min_interval
        self._last_price: PriceData | None = None
        self._last_fetch_monotonic: float = float("-inf")

    def get_price(self) -> PriceData:
        now = time.monotonic()
        cache_is_fresh = (now - self._last_fetch_monotonic) < self.min_interval
        if self._last_price is not None and cache_is_fresh:
            return self._last_price

        try:
            price = fetch_btc_price(timeout=self.timeout)
        except PriceFetchError:
            if self._last_price is not None:
                self._last_price = replace(self._last_price, is_stale=True)
                return self._last_price
            raise

        self._last_fetch_monotonic = now
        self._last_price = price
        return price
