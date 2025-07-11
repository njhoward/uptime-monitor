import csv
import time
import subprocess
from datetime import datetime

LOGFILE = "/var/log/uptime-monitor.csv"
HOST = "8.8.8.8"
INTERVAL = 30  # seconds

def is_up(host):
    return subprocess.call(["ping", "-c", "1", "-W", "2", host],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL) == 0

with open(LOGFILE, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    while True:
        status = "UP" if is_up(HOST) else "DOWN"
        writer.writerow([datetime.now().isoformat(), status])
        csvfile.flush()
        time.sleep(INTERVAL)
