from prometheus_client import Counter, Gauge, Histogram

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)
STUDENTS = Gauge("students_total", "Number of students stored in the database")
