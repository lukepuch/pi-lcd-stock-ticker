# Pi LCD Bitcoin Ticker

## Overview

A fullscreen Bitcoin price display for a Raspberry Pi driving a Waveshare
3.5" LCD (480x320). Shows the current BTC/USD price, 24h percent change
(green/red), and a last-updated timestamp, refreshing from a live API.

The project is intentionally small and split into two independent halves:

- **Data retrieval** (`ticker/bitcoin.py`, `ticker/data_source.py`,
  `ticker/models.py`) — fetches BTC/USD price and 24h change from
  [CoinGecko's free public API](https://www.coingecko.com/en/api) (no API
  key required), or a `MockDataSource` for offline UI work. A live fetch
  never happens more than once per 60 seconds, and if a fetch fails the
  last successful price is kept and shown with a "(stale)" indicator
  instead of crashing the display.
- **Display** (`ticker/display.py`) — a Tkinter UI that only knows how to
  render a `PriceData` object. It has no idea whether that data came from
  the real API or the mock source.

`main.py` wires the two together and is the entry point for both.

## Project layout

```
main.py                # entry point (CLI flags: --mock, --windowed)
ticker/
  models.py             # PriceData — the shape shared by every data source
  data_source.py         # MockDataSource, for offline UI dev
  bitcoin.py              # live CoinGecko fetch + stale-fallback caching
  display.py               # Tkinter UI, no data-fetching logic
tests/
  test_bitcoin.py          # pytest unit tests for the data layer (mocked, no network/GUI)
deploy/
  config.sh                 # Pi user/host/path — edit this to point at your Pi
  deploy.sh                  # rsyncs the repo to the Pi and runs it there
```

## Dev environment setup

Requires [`uv`](https://docs.astral.sh/uv/) and a system Python with
`tkinter` available (uv is pinned via `python-preference = "only-system"`
in `pyproject.toml`, since uv's managed Python builds don't include Tk and
`tkinter` isn't pip-installable).

```bash
# One-time: make sure tkinter is available to your system Python
sudo apt-get install -y python3-tk

# Install dependencies (currently just pytest, for tests) into .venv
uv sync
```

### Running locally

```bash
# Live data, windowed (won't take over your monitor)
uv run python main.py --windowed

# Mock data instead of hitting the real API
uv run python main.py --windowed --mock

# Fullscreen (as it runs on the Pi)
uv run python main.py
```

Press `Esc` to quit a running window.

### Running tests

```bash
uv run pytest tests/ -v
```

Tests fully mock the network layer (`urllib`) — no real HTTP calls, no
GUI required, safe to run anywhere.

## Deploying to a Pi

1. Edit `deploy/config.sh` with your Pi's SSH user/host and a target
   directory:

   ```bash
   PI_USER="pi"
   PI_HOST="raspberrypi.local"
   PI_DIR="/home/pi/pi-lcd-stock-ticker"
   PI_DISPLAY=":0"   # the Pi's own attached display, not your laptop's
   ```

2. One-time on the Pi itself, make sure `tkinter` is available there too:

   ```bash
   ssh <user>@<host> "sudo apt-get install -y python3-tk"
   ```

3. From your dev machine, deploy and run:

   ```bash
   ./deploy/deploy.sh
   ```

   This `rsync`s the repo to the Pi (excluding `.git/`, `__pycache__/`,
   `.pytest_cache/`) and then runs `python3 main.py` over SSH against the
   Pi's local display, so the UI shows up on the physical LCD. The app has
   no third-party runtime dependencies, so plain `python3` is enough on
   the Pi — `uv` isn't required there.

   `Ctrl+C` in your terminal stops the remote process. The Pi needs
   internet access to reach `api.coingecko.com`.
