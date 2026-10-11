import sqlite3

from flask import Blueprint, Response, current_app, jsonify, render_template, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import metrics
from .db import get_db

bp = Blueprint("main", __name__)

FIELDS = ("name", "email", "course")


def _validate(data, partial=False):
    """Return (clean_dict, error_message)."""
    if not isinstance(data, dict):
        return None, "JSON body required"
    clean = {k: str(data[k]).strip() for k in FIELDS if k in data and data[k] is not None}
    if not partial:
        for required in ("name", "email"):
            if not clean.get(required):
                return None, f"'{required}' is required"
    if "email" in clean and ("@" not in clean["email"] or "." not in clean["email"]):
        return None, "'email' is not a valid address"
    if "name" in clean and not clean["name"]:
        return None, "'name' cannot be empty"
    return clean, None


def _row(row):
    return dict(row) if row else None


@bp.get("/")
def index():
    return render_template("index.html", version=current_app.config["APP_VERSION"])


# ---------- CRUD ----------
@bp.get("/api/students")
def list_students():
    course = request.args.get("course")
    sql, args = "SELECT * FROM students", ()
    if course:
        sql, args = sql + " WHERE course = ?", (course,)
    rows = get_db().execute(sql + " ORDER BY id", args).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.post("/api/students")
def create_student():
    data, err = _validate(request.get_json(silent=True))
    if err:
        return jsonify(error=err), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (data["name"], data["email"], data.get("course", "")),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="a student with this email already exists"), 409
    row = db.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(_row(row)), 201


@bp.get("/api/students/<int:student_id>")
def get_student(student_id):
    row = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        return jsonify(error="student not found"), 404
    return jsonify(_row(row))


@bp.put("/api/students/<int:student_id>")
def update_student(student_id):
    data, err = _validate(request.get_json(silent=True), partial=True)
    if err:
        return jsonify(error=err), 400
    if not data:
        return jsonify(error="nothing to update"), 400
    db = get_db()
    if not db.execute("SELECT 1 FROM students WHERE id = ?", (student_id,)).fetchone():
        return jsonify(error="student not found"), 404
    assignments = ", ".join(f"{k} = ?" for k in data)  # keys come from FIELDS only
    try:
        db.execute(f"UPDATE students SET {assignments} WHERE id = ?", (*data.values(), student_id))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="a student with this email already exists"), 409
    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return jsonify(_row(row))


@bp.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    db = get_db()
    cur = db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="student not found"), 404
    return "", 204


# ---------- Operations endpoints ----------
@bp.get("/health")
def health():
    """Liveness: the process is up."""
    return jsonify(status="ok")


@bp.get("/ready")
def ready():
    """Readiness: the process can actually reach its database."""
    try:
        get_db().execute("SELECT 1").fetchone()
    except sqlite3.Error:
        return jsonify(status="database unavailable"), 503
    return jsonify(status="ready")


@bp.get("/version")
def version():
    return jsonify(
        version=current_app.config["APP_VERSION"], environment=current_app.config["APP_ENV"]
    )


@bp.get("/metrics")
def prometheus_metrics():
    count = get_db().execute("SELECT COUNT(*) FROM students").fetchone()[0]
    metrics.STUDENTS.set(count)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
