"""
Part 2: Full CRUD Operations with HTML Forms
=============================================
Complete Create, Read, Update, Delete operations with user forms.

What You'll Learn:
- HTML forms with POST method
- request.form to get form data
- UPDATE and DELETE SQL commands
- redirect() and url_for() functions
- Flash messages for user feedback

Prerequisites: Complete part-1 first
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from typing import Iterable

# Flask application instance
app = Flask(__name__)
app.secret_key = "your-secret-key-here"

# Path to the SQLite database file
STUDENTS_DB_PATH = "students.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a new SQLite connection with row access by column name.
    The caller is responsible for closing the connection or using a context manager.
    """
    connection = sqlite3.connect(STUDENTS_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Ensure the students table exists before the app starts serving requests."""
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL
            )
            """
        )
        connection.commit()


# =============================================================================
# CREATE - Add new student (with email validation)
# =============================================================================


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_name = request.form["name"]
        student_email = request.form["email"]
        student_course = request.form["course"]

        # Use a context manager to ensure the connection is cleaned up properly
        with get_db_connection() as connection:
            # 🔍 Check if email already exists
            existing_student = connection.execute(
                "SELECT * FROM students WHERE email = ?", (student_email,)
            ).fetchone()

            if existing_student:
                flash("Email already exists!", "danger")
                return redirect(url_for("add_student"))

            connection.execute(
                "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
                (student_name, student_email, student_course),
            )
            connection.commit()

        flash("Student added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


# =============================================================================
# READ + SEARCH
# =============================================================================


@app.route("/")
def index():
    search_query = request.args.get("search")

    with get_db_connection() as connection:
        if search_query:
            students: Iterable[sqlite3.Row] = connection.execute(
                "SELECT * FROM students WHERE name LIKE ? ORDER BY id DESC",
                ("%" + search_query + "%",),
            ).fetchall()
        else:
            students = connection.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()

    return render_template(
        "index.html",
        students=students,
        search_query=search_query,
    )


# =============================================================================
# UPDATE
# =============================================================================


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if request.method == "POST":
        updated_name = request.form["name"]
        updated_email = request.form["email"]
        updated_course = request.form["course"]

        with get_db_connection() as connection:
            connection.execute(
                "UPDATE students SET name = ?, email = ?, course = ? WHERE id = ?",
                (updated_name, updated_email, updated_course, id),
            )
            connection.commit()

        flash("Student updated successfully!", "success")
        return redirect(url_for("index"))

    with get_db_connection() as connection:
        student = connection.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

    return render_template("edit.html", student=student)


# =============================================================================
# DELETE
# =============================================================================


@app.route("/delete/<int:id>")
def delete_student(id):
    with get_db_connection() as connection:
        connection.execute("DELETE FROM students WHERE id = ?", (id,))
        connection.commit()

    flash("Student deleted!", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)


# =============================================================================
# CRUD SUMMARY:
# =============================================================================
#
# Operation | HTTP Method | SQL Command | Route Example
# ----------|-------------|-------------|---------------
# Create    | POST        | INSERT INTO | /add
# Read      | GET         | SELECT      | / or /student/1
# Update    | POST        | UPDATE      | /edit/1
# Delete    | GET/POST    | DELETE      | /delete/1
#
# =============================================================================
# NEW CONCEPTS:
# =============================================================================
#
# 1. methods=['GET', 'POST']
#    - GET: Display the form (empty or with current data)
#    - POST: Process the submitted form
#
# 2. request.form['field_name']
#    - Gets the value from HTML form input with that name
#
# 3. redirect(url_for('function_name'))
#    - Sends user to another page after action completes
#
# 4. flash('message', 'category')
#    - Shows one-time message to user
#    - Categories: 'success', 'danger', 'warning', 'info'
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add a "Search" feature to find students by name
# 2. Add validation to check if email already exists before adding
#
# =============================================================================
