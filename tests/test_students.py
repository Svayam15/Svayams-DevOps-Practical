def test_create_student(client):
    r = client.post("/api/students", json={"name": "Ravi", "email": "ravi@example.com", "course": "MSc IT"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1 and body["name"] == "Ravi" and body["course"] == "MSc IT"


def test_list_students(client, sample):
    r = client.get("/api/students")
    assert r.status_code == 200
    assert [s["email"] for s in r.get_json()] == ["asha@example.com"]


def test_filter_by_course(client, sample):
    client.post("/api/students", json={"name": "B", "email": "b@example.com", "course": "MBA"})
    r = client.get("/api/students?course=MBA")
    assert [s["name"] for s in r.get_json()] == ["B"]


def test_get_student(client, sample):
    assert client.get(f"/api/students/{sample['id']}").get_json()["name"] == "Asha Rao"


def test_get_missing_student_returns_404(client):
    assert client.get("/api/students/999").status_code == 404


def test_update_student(client, sample):
    r = client.put(f"/api/students/{sample['id']}", json={"course": "MSc CS"})
    assert r.status_code == 200
    assert r.get_json()["course"] == "MSc CS"
    assert r.get_json()["name"] == "Asha Rao"  # untouched fields stay


def test_update_missing_student_returns_404(client):
    assert client.put("/api/students/42", json={"name": "x"}).status_code == 404


def test_delete_student(client, sample):
    assert client.delete(f"/api/students/{sample['id']}").status_code == 204
    assert client.get(f"/api/students/{sample['id']}").status_code == 404


def test_delete_missing_student_returns_404(client):
    assert client.delete("/api/students/42").status_code == 404


def test_duplicate_email_rejected(client, sample):
    r = client.post("/api/students", json={"name": "Other", "email": "asha@example.com"})
    assert r.status_code == 409


def test_update_to_duplicate_email_rejected(client, sample):
    other = client.post("/api/students", json={"name": "O", "email": "o@example.com"}).get_json()
    r = client.put(f"/api/students/{other['id']}", json={"email": "asha@example.com"})
    assert r.status_code == 409


def test_missing_required_fields(client):
    assert client.post("/api/students", json={"name": "NoEmail"}).status_code == 400
    assert client.post("/api/students", json={"email": "a@b.com"}).status_code == 400


def test_invalid_email(client):
    assert client.post("/api/students", json={"name": "X", "email": "not-an-email"}).status_code == 400


def test_non_json_body(client):
    assert client.post("/api/students", data="plain text").status_code == 400


def test_empty_update_rejected(client, sample):
    assert client.put(f"/api/students/{sample['id']}", json={}).status_code == 400
