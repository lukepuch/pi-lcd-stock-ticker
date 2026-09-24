import argparse

from ticker.bitcoin import BitcoinDataSource
from ticker.data_source import MockDataSource
from ticker.display import TickerDisplay

LIVE_REFRESH_MS = 60_000
MOCK_REFRESH_MS = 5_000


def main():
    parser = argparse.ArgumentParser(description="Bitcoin LCD ticker")
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in a normal window instead of fullscreen (for dev testing)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data instead of the real API (for offline UI dev)",
    )
    args = parser.parse_args()

    if args.mock:
        data_source = MockDataSource()
        refresh_ms = MOCK_REFRESH_MS
    else:
        data_source = BitcoinDataSource()
        refresh_ms = LIVE_REFRESH_MS

    app = TickerDisplay(data_source, fullscreen=not args.windowed, refresh_ms=refresh_ms)
    app.mainloop()


if __name__ == "__main__":
    main()
