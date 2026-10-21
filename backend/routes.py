"""REST API endpoints. All responses use a consistent JSON envelope."""
from flask import Blueprint, jsonify, request

import models
from database import get_db

api = Blueprint("api", __name__, url_prefix="/api")


def success(data=None, message=None, status=200, **extra):
    body = {"success": True, "message": message, "data": data}
    body.update(extra)
    return jsonify(body), status


def error(code, message, status, details=None):
    return jsonify({"success": False,
                    "error": {"code": code, "message": message, "details": details or {}}}), status


def read_payload():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


@api.get("/health")
def health():
    try:
        get_db().execute("SELECT 1").fetchone()
    except Exception:
        return error("DB_UNAVAILABLE", "Database is not reachable.", 503)
    return success({"status": "ok", "database": "ok"}, "Service is healthy.")


@api.get("/students")
def list_students():
    students = models.list_students(request.args.get("search", ""))
    return success(students, count=len(students), total=models.count_students())


@api.get("/students/<int:record_id>")
def get_student(record_id):
    student = models.get_student(record_id)
    if student is None:
        return error("NOT_FOUND", "Student not found.", 404)
    return success(student)


@api.post("/students")
def create_student():
    payload = read_payload()
    if payload is None:
        return error("INVALID_JSON", "Request body must be a JSON object.", 400)
    cleaned, errors = models.validate_student(payload)
    if errors:
        return error("VALIDATION_ERROR", "Please correct the highlighted fields.", 400, errors)
    try:
        student = models.create_student(cleaned)
    except models.DuplicateError as exc:
        return error("DUPLICATE", "Student already exists.", 409, exc.errors)
    return success(student, "Student added successfully.", 201)


@api.put("/students/<int:record_id>")
def update_student(record_id):
    payload = read_payload()
    if payload is None:
        return error("INVALID_JSON", "Request body must be a JSON object.", 400)
    cleaned, errors = models.validate_student(payload)
    if errors:
        return error("VALIDATION_ERROR", "Please correct the highlighted fields.", 400, errors)
    try:
        student = models.update_student(record_id, cleaned)
    except models.DuplicateError as exc:
        return error("DUPLICATE", "Student already exists.", 409, exc.errors)
    if student is None:
        return error("NOT_FOUND", "Student not found.", 404)
    return success(student, "Student updated successfully.")


@api.delete("/students/<int:record_id>")
def delete_student(record_id):
    if not models.delete_student(record_id):
        return error("NOT_FOUND", "Student not found.", 404)
    return success(None, "Student deleted successfully.")
