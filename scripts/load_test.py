"""Tiny traffic generator (stdlib only) for demoing Grafana graphs and the HPA.

    python scripts/load_test.py http://<minikube-ip>:<nodeport> [seconds] [threads]
"""
import sys
import threading
import time
import urllib.error
import urllib.request

url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 60
threads = int(sys.argv[3]) if len(sys.argv) > 3 else 8
stop = time.time() + seconds
counts = {"ok": 0, "err": 0}
lock = threading.Lock()


def worker():
    while time.time() < stop:
        try:
            urllib.request.urlopen(url + "/api/students", timeout=5).read()
            key = "ok"
        except (urllib.error.URLError, OSError):
            key = "err"
        with lock:
            counts[key] += 1


pool = [threading.Thread(target=worker) for _ in range(threads)]
[t.start() for t in pool]
[t.join() for t in pool]
print(f"done: {counts['ok']} ok, {counts['err']} errors in {seconds}s with {threads} threads")
