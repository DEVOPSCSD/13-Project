"""Selenium end-to-end tests (Chrome). The application must already be running.

BASE_URL  : address of the app (default http://localhost:5000)
HEADLESS  : "true" (default) runs Chrome without a window; "false" shows the browser

Every test creates students with a unique random ID and removes them afterwards,
so normal demo records are never touched.
"""
import os
import uuid

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000").rstrip("/")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"


@pytest.fixture(scope="session")
def driver():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,1000")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=opts)   # Selenium Manager downloads ChromeDriver itself
    yield drv
    drv.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)


@pytest.fixture
def student():
    """Unique student data; deleted through the API after the test."""
    token = uuid.uuid4().hex[:8]
    data = {"student_id": "SEL-" + token.upper(), "full_name": "Selenium " + token,
            "email": f"sel.{token}@example.com", "course": "QA Testing " + token,
            "year_of_study": 3, "phone": "9000000000"}
    yield data
    try:
        rows = requests.get(f"{BASE_URL}/api/students", params={"search": token}, timeout=10).json()["data"]
        for row in rows:
            requests.delete(f"{BASE_URL}/api/students/{row['id']}", timeout=10)
    except requests.RequestException:
        pass


@pytest.fixture
def page(driver, wait):
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.ID, "student-form")))
    wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
    return driver


def fill_form(driver, d):
    for el_id, key in [("input-student-id", "student_id"), ("input-full-name", "full_name"),
                       ("input-email", "email"), ("input-course", "course"), ("input-phone", "phone")]:
        field = driver.find_element(By.ID, el_id)
        field.clear()
        field.send_keys(d[key])
    Select(driver.find_element(By.ID, "input-year")).select_by_value(str(d["year_of_study"]))


def row_for(driver, student_id):
    return (By.CSS_SELECTOR, f'tr[data-student-id="{student_id}"]')


def add_student(driver, wait, d):
    fill_form(driver, d)
    driver.find_element(By.ID, "btn-submit").click()
    wait.until(EC.presence_of_element_located(row_for(driver, d["student_id"])))


def test_website_opens(page):
    assert "Student Management" in page.title


def test_registration_form_visible(page):
    assert page.find_element(By.ID, "student-form").is_displayed()
    assert page.find_element(By.ID, "btn-submit").is_displayed()


def test_add_student_appears_in_directory(page, wait, student):
    add_student(page, wait, student)
    wait.until(EC.text_to_be_present_in_element((By.ID, "toast"), "added successfully"))
    assert student["full_name"] in page.find_element(*row_for(page, student["student_id"])).text


def test_search_filters_records(page, wait, student):
    add_student(page, wait, student)
    box = page.find_element(By.ID, "search-input")
    box.clear()
    box.send_keys(student["course"])
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#students-table-body tr")) == 1)
    assert page.find_element(*row_for(page, student["student_id"])).is_displayed()
    box.clear()
    box.send_keys("no-such-student-xyz")
    wait.until(EC.visibility_of_element_located((By.ID, "empty-state")))


def test_invalid_submission_shows_errors(page, wait):
    page.find_element(By.ID, "input-email").send_keys("not-an-email")
    page.find_element(By.ID, "btn-submit").click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "error-email"), "valid email"))
    assert page.find_element(By.ID, "error-student_id").text != ""
    assert page.find_element(By.ID, "toast").is_displayed()


def test_edit_student(page, wait, student):
    add_student(page, wait, student)
    row = page.find_element(*row_for(page, student["student_id"]))
    row.find_element(By.CSS_SELECTOR, 'button[data-action="edit"]').click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "form-title"), "Edit student"))
    name = page.find_element(By.ID, "input-full-name")
    name.clear()
    name.send_keys("Edited Name")
    page.find_element(By.ID, "btn-submit").click()
    wait.until(EC.text_to_be_present_in_element((By.ID, "toast"), "updated successfully"))
    wait.until(lambda d: "Edited Name" in d.find_element(*row_for(d, student["student_id"])).text)


def test_delete_student(page, wait, student):
    add_student(page, wait, student)
    row = page.find_element(*row_for(page, student["student_id"]))
    row.find_element(By.CSS_SELECTOR, 'button[data-action="delete"]').click()
    wait.until(EC.element_to_be_clickable((By.ID, "confirm-yes"))).click()
    wait.until(EC.invisibility_of_element_located(row_for(page, student["student_id"])))
