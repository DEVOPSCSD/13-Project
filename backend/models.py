"""Student validation rules and database operations."""
import re
import sqlite3

from database import get_db

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
STUDENT_ID_RE = re.compile(r"^[A-Za-z0-9\-]{3,20}$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")
COLUMNS = "id, student_id, full_name, email, course, year_of_study, phone, created_at"


class DuplicateError(Exception):
    """Raised when student_id or email already exists."""

    def __init__(self, errors):
        super().__init__("Duplicate student")
        self.errors = errors


def validate_student(data):
    """Return (cleaned_data, errors). errors is a dict {field: message}."""
    errors, cleaned = {}, {}

    def text(field, label, min_len, max_len):
        value = data.get(field)
        value = value.strip() if isinstance(value, str) else ""
        if not value:
            errors[field] = f"{label} is required."
        elif not (min_len <= len(value) <= max_len):
            errors[field] = f"{label} must be {min_len}-{max_len} characters."
        return value

    sid = text("student_id", "Student ID", 3, 20)
    if sid and "student_id" not in errors:
        if not STUDENT_ID_RE.match(sid):
            errors["student_id"] = "Student ID may contain only letters, digits and hyphens."
        else:
            cleaned["student_id"] = sid.upper()

    name = text("full_name", "Full name", 2, 100)
    if name and "full_name" not in errors:
        cleaned["full_name"] = name

    email = text("email", "Email", 5, 120)
    if email and "email" not in errors:
        if not EMAIL_RE.match(email):
            errors["email"] = "Enter a valid email address."
        else:
            cleaned["email"] = email.lower()

    course = text("course", "Course", 2, 100)
    if course and "course" not in errors:
        cleaned["course"] = course

    year = data.get("year_of_study")
    if isinstance(year, bool):
        year = None
    if isinstance(year, str) and year.strip().isdigit():
        year = int(year.strip())
    if year is None or year == "":
        errors["year_of_study"] = "Year of study is required."
    elif not isinstance(year, int) or not (1 <= year <= 6):
        errors["year_of_study"] = "Year of study must be a number from 1 to 6."
    else:
        cleaned["year_of_study"] = year

    phone = data.get("phone")
    phone = phone.strip() if isinstance(phone, str) else ""
    if phone and not PHONE_RE.match(phone):
        errors["phone"] = "Phone may contain digits, spaces, + - ( ) and be 7-20 characters."
    else:
        cleaned["phone"] = phone

    return cleaned, errors


def _escape_like(term):
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def count_students():
    return get_db().execute("SELECT COUNT(*) FROM students").fetchone()[0]


def list_students(search=None):
    sql = f"SELECT {COLUMNS} FROM students"
    params = []
    if search and search.strip():
        like = f"%{_escape_like(search.strip())}%"
        sql += (" WHERE full_name LIKE ? ESCAPE '\\' OR email LIKE ? ESCAPE '\\'"
                " OR course LIKE ? ESCAPE '\\' OR student_id LIKE ? ESCAPE '\\'")
        params = [like, like, like, like]
    sql += " ORDER BY id DESC"
    return [dict(r) for r in get_db().execute(sql, params).fetchall()]


def get_student(record_id):
    row = get_db().execute(f"SELECT {COLUMNS} FROM students WHERE id = ?", (record_id,)).fetchone()
    return dict(row) if row else None


def _check_duplicates(data, exclude_id=-1):
    rows = get_db().execute(
        "SELECT student_id, email FROM students WHERE (student_id = ? OR email = ?) AND id != ?",
        (data["student_id"], data["email"], exclude_id)).fetchall()
    errors = {}
    for row in rows:
        if row["student_id"] == data["student_id"]:
            errors["student_id"] = "This Student ID already exists."
        if row["email"] == data["email"]:
            errors["email"] = "This email is already registered."
    if errors:
        raise DuplicateError(errors)


def create_student(data):
    _check_duplicates(data)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO students (student_id, full_name, email, course, year_of_study, phone) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (data["student_id"], data["full_name"], data["email"],
             data["course"], data["year_of_study"], data["phone"]))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise DuplicateError({"student_id": "Student ID or email already exists."})
    return get_student(cur.lastrowid)


def update_student(record_id, data):
    if get_student(record_id) is None:
        return None
    _check_duplicates(data, exclude_id=record_id)
    db = get_db()
    try:
        db.execute(
            "UPDATE students SET student_id = ?, full_name = ?, email = ?, "
            "course = ?, year_of_study = ?, phone = ? WHERE id = ?",
            (data["student_id"], data["full_name"], data["email"],
             data["course"], data["year_of_study"], data["phone"], record_id))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise DuplicateError({"student_id": "Student ID or email already exists."})
    return get_student(record_id)


def delete_student(record_id):
    db = get_db()
    cur = db.execute("DELETE FROM students WHERE id = ?", (record_id,))
    db.commit()
    return cur.rowcount > 0
