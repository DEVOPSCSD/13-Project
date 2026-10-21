/* Frontend logic. Talks to the Flask REST API only through /api/... (the stable contract). */
const API = "/api/students";
const FIELDS = {
  student_id: "input-student-id", full_name: "input-full-name", email: "input-email",
  course: "input-course", year_of_study: "input-year", phone: "input-phone",
};
const $ = (id) => document.getElementById(id);
const EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/;

let students = [];
let pendingDeleteId = null;
let toastTimer = null;
let searchTimer = null;

function escapeHtml(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function toast(message, type = "success") {
  const t = $("toast");
  t.textContent = message;
  t.className = "toast " + type;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 4000);
}

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" }, ...options,
  });
  let body = null;
  try { body = await res.json(); } catch (e) { /* non-JSON response */ }
  if (!res.ok || !body || body.success === false) {
    const err = new Error(body?.error?.message || "Request failed (" + res.status + ")");
    err.details = body?.error?.details || {};
    throw err;
  }
  return body;
}

/* ---------- list / render ---------- */
async function loadStudents() {
  const search = $("search-input").value.trim();
  $("loading").classList.remove("hidden");
  $("empty-state").classList.add("hidden");
  try {
    const body = await api(API + (search ? "?search=" + encodeURIComponent(search) : ""));
    students = body.data;
    $("stat-total").textContent = body.total;
    $("stat-shown").textContent = body.count;
    render();
  } catch (e) {
    toast("Could not load students: " + e.message, "error");
  } finally {
    $("loading").classList.add("hidden");
  }
}

function render() {
  const body = $("students-table-body");
  body.innerHTML = students.map((s) => `
    <tr data-student-id="${escapeHtml(s.student_id)}">
      <td>${escapeHtml(s.student_id)}</td>
      <td>${escapeHtml(s.full_name)}</td>
      <td>${escapeHtml(s.email)}</td>
      <td>${escapeHtml(s.course)}</td>
      <td>${escapeHtml(s.year_of_study)}</td>
      <td>${escapeHtml(s.phone || "-")}</td>
      <td>
        <button class="btn small" id="edit-${s.id}" data-action="edit" data-id="${s.id}">Edit</button>
        <button class="btn small danger" id="delete-${s.id}" data-action="delete" data-id="${s.id}">Delete</button>
      </td>
    </tr>`).join("");
  $("empty-state").classList.toggle("hidden", students.length > 0);
  $("students-table").classList.toggle("hidden", students.length === 0);
}

/* ---------- form ---------- */
function clearErrors() {
  Object.keys(FIELDS).forEach((k) => {
    $("error-" + k).textContent = "";
    $(FIELDS[k]).classList.remove("invalid");
  });
}

function showErrors(errors) {
  Object.entries(errors).forEach(([k, msg]) => {
    if (!$("error-" + k)) return;
    $("error-" + k).textContent = msg;
    $(FIELDS[k]).classList.add("invalid");
  });
}

function readForm() {
  const data = {};
  Object.entries(FIELDS).forEach(([k, id]) => (data[k] = $(id).value.trim()));
  return data;
}

function validateForm(d) {
  const e = {};
  if (!d.student_id) e.student_id = "Student ID is required.";
  else if (!/^[A-Za-z0-9\-]{3,20}$/.test(d.student_id)) e.student_id = "Use 3-20 letters, digits or hyphens.";
  if (!d.full_name) e.full_name = "Full name is required.";
  if (!d.email) e.email = "Email is required.";
  else if (!EMAIL_RE.test(d.email)) e.email = "Enter a valid email address.";
  if (!d.course) e.course = "Course is required.";
  if (!d.year_of_study) e.year_of_study = "Year of study is required.";
  if (d.phone && !/^[0-9+\-\s()]{7,20}$/.test(d.phone)) e.phone = "Enter a valid phone number.";
  return e;
}

function resetForm() {
  $("student-form").reset();
  $("record-id").value = "";
  $("form-title").textContent = "Register student";
  $("btn-submit").textContent = "Add student";
  $("btn-cancel").classList.add("hidden");
  clearErrors();
}

async function onSubmit(ev) {
  ev.preventDefault();
  clearErrors();
  const data = readForm();
  const errors = validateForm(data);
  if (Object.keys(errors).length) {
    showErrors(errors);
    toast("Please correct the highlighted fields.", "error");
    return;
  }
  data.year_of_study = parseInt(data.year_of_study, 10);
  const id = $("record-id").value;
  try {
    const body = await api(id ? API + "/" + id : API, {
      method: id ? "PUT" : "POST", body: JSON.stringify(data),
    });
    toast(body.message, "success");
    resetForm();
    await loadStudents();
  } catch (e) {
    showErrors(e.details || {});
    toast(e.message, "error");
  }
}

function startEdit(id) {
  const s = students.find((x) => x.id === id);
  if (!s) return;
  clearErrors();
  $("record-id").value = s.id;
  Object.entries(FIELDS).forEach(([k, el]) => ($(el).value = s[k] ?? ""));
  $("form-title").textContent = "Edit student";
  $("btn-submit").textContent = "Update student";
  $("btn-cancel").classList.remove("hidden");
  $("form-section").scrollIntoView({ behavior: "smooth" });
}

/* ---------- delete ---------- */
function askDelete(id) {
  const s = students.find((x) => x.id === id);
  pendingDeleteId = id;
  $("confirm-text").textContent = "Delete " + (s ? s.full_name : "this student") + "?";
  $("confirm-modal").classList.remove("hidden");
}

async function confirmDelete() {
  const id = pendingDeleteId;
  $("confirm-modal").classList.add("hidden");
  pendingDeleteId = null;
  try {
    const body = await api(API + "/" + id, { method: "DELETE" });
    toast(body.message, "success");
    if ($("record-id").value === String(id)) resetForm();
    await loadStudents();
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ---------- wiring ---------- */
document.addEventListener("DOMContentLoaded", () => {
  $("student-form").addEventListener("submit", onSubmit);
  $("btn-cancel").addEventListener("click", resetForm);
  $("confirm-yes").addEventListener("click", confirmDelete);
  $("confirm-no").addEventListener("click", () => $("confirm-modal").classList.add("hidden"));
  $("search-input").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadStudents, 250);
  });
  $("students-table-body").addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-action]");
    if (!btn) return;
    const id = parseInt(btn.dataset.id, 10);
    if (btn.dataset.action === "edit") startEdit(id);
    else askDelete(id);
  });
  loadStudents();
});
