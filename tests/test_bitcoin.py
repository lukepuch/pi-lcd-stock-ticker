import json
from urllib.error import URLError

import pytest

from ticker.bitcoin import BitcoinDataSource, PriceFetchError, fetch_btc_price
from ticker.models import PriceData


class _FakeResponse:
    """Stands in for the object urlopen() returns as a context manager."""

    def __init__(self, payload_bytes: bytes):
        self._payload_bytes = payload_bytes

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self):
        return self._payload_bytes


def _make_price(price_usd=65000.0, is_stale=False):
    return PriceData(
        symbol="BTC", name="BITCOIN", price_usd=price_usd,
        change_24h_pct=1.0, last_updated=None, is_stale=is_stale,
    )


# --- fetch_btc_price ---

def test_fetch_success_returns_price_data(monkeypatch):
    payload = json.dumps({"bitcoin": {"usd": 65000.5, "usd_24h_change": 1.23}}).encode()
    monkeypatch.setattr("ticker.bitcoin.urlopen", lambda *a, **k: _FakeResponse(payload))

    result = fetch_btc_price()

    assert result.symbol == "BTC"
    assert result.price_usd == 65000.5
    assert result.change_24h_pct == 1.23
    assert result.is_stale is False


def test_fetch_network_error_raises_price_fetch_error(monkeypatch):
    def raise_error(*a, **k):
        raise URLError("no route")

    monkeypatch.setattr("ticker.bitcoin.urlopen", raise_error)

    with pytest.raises(PriceFetchError):
        fetch_btc_price()


def test_fetch_malformed_json_raises_price_fetch_error(monkeypatch):
    monkeypatch.setattr("ticker.bitcoin.urlopen", lambda *a, **k: _FakeResponse(b"not json"))

    with pytest.raises(PriceFetchError):
        fetch_btc_price()


def test_fetch_missing_key_raises_price_fetch_error(monkeypatch):
    payload = json.dumps({"unexpected": {}}).encode()
    monkeypatch.setattr("ticker.bitcoin.urlopen", lambda *a, **k: _FakeResponse(payload))

    with pytest.raises(PriceFetchError):
        fetch_btc_price()


# --- BitcoinDataSource ---

def test_source_returns_fresh_price_on_success(monkeypatch):
    calls = []

    def fake_fetch(timeout):
        calls.append(timeout)
        return _make_price()

    monkeypatch.setattr("ticker.bitcoin.fetch_btc_price", fake_fetch)
    source = BitcoinDataSource(min_interval=0)

    result = source.get_price()

    assert len(calls) == 1
    assert result.is_stale is False
    assert result.price_usd == 65000.0


def test_source_does_not_refetch_within_min_interval(monkeypatch):
    calls = []

    def fake_fetch(timeout):
        calls.append(timeout)
        return _make_price()

    monkeypatch.setattr("ticker.bitcoin.fetch_btc_price", fake_fetch)
    source = BitcoinDataSource(min_interval=1000)

    source.get_price()
    source.get_price()

    assert len(calls) == 1


def test_source_falls_back_to_stale_price_on_failure(monkeypatch):
    source = BitcoinDataSource(min_interval=0)

    monkeypatch.setattr("ticker.bitcoin.fetch_btc_price", lambda timeout: _make_price(price_usd=65000.0))
    first = source.get_price()

    def raise_error(timeout):
        raise PriceFetchError("down")

    monkeypatch.setattr("ticker.bitcoin.fetch_btc_price", raise_error)
    second = source.get_price()

    assert second.is_stale is True
    assert second.price_usd == first.price_usd


def test_source_raises_when_no_cache_and_fetch_fails(monkeypatch):
    def raise_error(timeout):
        raise PriceFetchError("down")

    monkeypatch.setattr("ticker.bitcoin.fetch_btc_price", raise_error)
    source = BitcoinDataSource(min_interval=0)

    with pytest.raises(PriceFetchError):
        source.get_price()
