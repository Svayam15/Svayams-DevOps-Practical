"""Tiny traffic generator (stdlib only) for demoing Grafana graphs and the HPA.

    python scripts/generate_load.py http://<minikube-url> [seconds] [threads]
"""
import sys
import threading
import time
import urllib.error
import urllib.request


def worker(url, stop_at, counts, lock):
    while time.time() < stop_at:
        try:
            urllib.request.urlopen(url + "/api/students", timeout=5).read()
            key = "ok"
        except (urllib.error.URLError, OSError):
            key = "err"
        with lock:
            counts[key] += 1


def main():
    url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:5000"
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    counts, lock = {"ok": 0, "err": 0}, threading.Lock()
    stop_at = time.time() + seconds
    pool = [threading.Thread(target=worker, args=(url, stop_at, counts, lock)) for _ in range(threads)]
    for t in pool:
        t.start()
    for t in pool:
        t.join()
    print(f"done: {counts['ok']} ok, {counts['err']} errors in {seconds}s with {threads} threads")


if __name__ == "__main__":
    main()
