# Shared configuration for scripts in deploy/. Edit to match your Pi,
# or override any value via environment variable when invoking a script.
PI_USER="${PI_USER:-luke}"
PI_HOST="${PI_HOST:-muffin.local}"
PI_DIR="${PI_DIR:-/home/${PI_USER}/pi-lcd-stock-ticker}"

# The Pi's LCD is on its local X display, not the SSH session's own display.
PI_DISPLAY="${PI_DISPLAY:-:0}"
