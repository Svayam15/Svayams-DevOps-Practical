def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.get_json() == {"status": "ok"}


def test_ready(client):
    assert client.get("/ready").get_json() == {"status": "ready"}


def test_version(client):
    body = client.get("/version").get_json()
    assert "version" in body and "environment" in body


def test_home_page_renders(client):
    r = client.get("/")
    assert r.status_code == 200 and b"Student Management System" in r.data


def test_metrics_exposed(client, sample):
    client.get("/api/students")
    text = client.get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in text
    assert "http_request_duration_seconds" in text
    assert "students_total 1.0" in text


def test_ui_reads_form_fields_explicitly(client):
    # Regression: bare `name.value` resolves to window.name in browsers, so the
    # name was never sent. The page must look inputs up by id.
    html = client.get("/").get_data(as_text=True)
    assert "name.value" not in html.replace("field('name')", "")
    assert "document.getElementById(id).value" in html