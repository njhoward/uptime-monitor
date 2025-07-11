import csv
import os
import time
import subprocess
from datetime import datetime

LOGFILE        = "/home/debian/logs/uptime-monitor.csv"
HOST           = "8.8.8.8"
INTERVAL       = 30     # seconds while UP
DOWN_INTERVAL  = 5      # seconds while DOWN

def ping_once(host: str, timeout: int = 2):
    """
    Returns (is_up: bool, rtt_ms: float|None).
    rtt_ms is None when host is unreachable.
    """
    result = subprocess.run(
        ["ping", "-c", "1", "-W", str(timeout), host],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        # Look for 'time=12.3 ms' in the output
        for line in result.stdout.splitlines():
            if "time=" in line:
                try:
                    rtt_str = line.split("time=")[1].split()[0]  # up to 'ms'
                    return True, float(rtt_str)
                except (IndexError, ValueError):
                    break
        return True, None  # Shouldn’t happen, but safety first
    else:
        return False, None

# Create file with header if it doesn't exist yet
if not os.path.exists(LOGFILE):
    with open(LOGFILE, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp", "status", "rtt_ms"])

current_interval = INTERVAL
prev_status      = "UNKNOWN"

with open(LOGFILE, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)

    while True:
        up, rtt = ping_once(HOST)
        status = "UP" if up else "DOWN"

        # Log every DOWN poll, or when status changes, or when RTT is recorded
        if status != prev_status or status == "DOWN":
            writer.writerow([datetime.now().isoformat(), status, rtt])
            csvfile.flush()
            prev_status = status
        elif status == "UP":        # still up, but we may want RTT trend
            writer.writerow([datetime.now().isoformat(), status, rtt])
            csvfile.flush()

        current_interval = DOWN_INTERVAL if status == "DOWN" else INTERVAL
        time.sleep(current_interval)
