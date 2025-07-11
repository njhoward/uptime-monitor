import csv
import time
import subprocess
from datetime import datetime

LOGFILE        = "/home/debian/logs/uptime-monitor.csv"
HOST           = "8.8.8.8"
INTERVAL       = 30    # normal polling interval (seconds)
DOWN_INTERVAL  = 5     # faster polling while offline (seconds)

def is_up(host: str) -> bool:
    """Ping host once with 2-second timeout. Return True if reachable."""
    return subprocess.call(
        ["ping", "-c", "1", "-W", "2", host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0

current_interval = INTERVAL          # start in normal mode
prev_status      = "UNKNOWN"         # ensure first entry is always written

with open(LOGFILE, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)

    while True:
        status = "UP" if is_up(HOST) else "DOWN"

        # Log only when status changes OR at each poll when already DOWN
        if status != prev_status or status == "DOWN":
            writer.writerow([datetime.now().isoformat(), status])
            csvfile.flush()
            prev_status = status

        # Adjust interval based on current status
        current_interval = DOWN_INTERVAL if status == "DOWN" else INTERVAL
        time.sleep(current_interval)
