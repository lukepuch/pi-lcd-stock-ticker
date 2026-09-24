import sys
import tkinter as tk

from ticker.models import PriceData

BG_COLOR = "#0d1117"
FG_COLOR = "#e6edf3"
GREEN = "#3fb950"
RED = "#f85149"
MUTED = "#8b949e"
STALE = "#d29922"


class TickerDisplay(tk.Tk):
    """Fullscreen 480x320 Bitcoin price display. Has no knowledge of
    where PriceData comes from — it just renders whatever get_price() returns,
    and tolerates get_price() raising (e.g. no network yet) without crashing.
    """

    def __init__(self, data_source, fullscreen: bool = True, refresh_ms: int = 5000):
        super().__init__()
        self.data_source = data_source
        self.refresh_ms = refresh_ms

        self.title("Bitcoin Ticker")
        self.geometry("480x320")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        if fullscreen:
            self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _event: self.destroy())

        self._build_widgets()
        self._refresh()

    def _build_widgets(self):
        self.name_label = tk.Label(
            self, text="BITCOIN / BTC", font=("DejaVu Sans", 20, "bold"),
            fg=MUTED, bg=BG_COLOR,
        )
        self.name_label.pack(pady=(24, 0))

        self.price_label = tk.Label(
            self, text="$0.00", font=("DejaVu Sans", 52, "bold"),
            fg=FG_COLOR, bg=BG_COLOR,
        )
        self.price_label.pack(pady=(16, 0))

        self.change_label = tk.Label(
            self, text="0.00%", font=("DejaVu Sans", 28, "bold"),
            fg=GREEN, bg=BG_COLOR,
        )
        self.change_label.pack(pady=(12, 0))

        self.updated_label = tk.Label(
            self, text="Last updated: --:--:--", font=("DejaVu Sans", 12),
            fg=MUTED, bg=BG_COLOR,
        )
        self.updated_label.pack(side="bottom", pady=(0, 16))

    def _refresh(self):
        try:
            data = self.data_source.get_price()
        except Exception as exc:
            print(f"price fetch failed: {exc}", file=sys.stderr)
            self.updated_label.config(text="Waiting for data...", fg=STALE)
        else:
            self._render(data)
        finally:
            self.after(self.refresh_ms, self._refresh)

    def _render(self, data: PriceData):
        self.price_label.config(text=f"${data.price_usd:,.2f}")

        sign = "+" if data.change_24h_pct >= 0 else ""
        color = GREEN if data.change_24h_pct >= 0 else RED
        self.change_label.config(text=f"{sign}{data.change_24h_pct:.2f}%", fg=color)

        timestamp = data.last_updated.strftime("%H:%M:%S")
        if data.is_stale:
            self.updated_label.config(text=f"Last updated: {timestamp} (stale)", fg=STALE)
        else:
            self.updated_label.config(text=f"Last updated: {timestamp}", fg=MUTED)
