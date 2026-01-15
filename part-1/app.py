from flask import Flask, render_template
import sqlite3

# Create the Flask application instance
app = Flask(__name__)

# SQLite database file name
STUDENTS_DB_FILE = "students.db"


def get_db_connection():
    """
    Create and return a database connection.
    row_factory allows accessing columns by name instead of index.
    """
    conn = sqlite3.connect(STUDENTS_DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database.
    Creates the 'students' table if it does not already exist.
    This function runs once when the app starts.
    """
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    """
    Home page route.
    Fetches all students from the database
    and passes them to the HTML template.
    """
    conn = get_db_connection()

    # Retrieve all student records
    students_list = conn.execute("SELECT * FROM students").fetchall()

    conn.close()

    # Render index.html and send students data to it
    return render_template("index.html", students=students_list)


@app.route("/add")
def add_sample_student():
    """
    Adds one sample student to the database.
    Each request adds the next student from the sample list.
    """

    # Predefined list of sample students for Exercise 
    sample_students = [
        ("Student 1", "student1@example.com", "Flask + Databases"),
        ("Student 2", "student2@example.com", "Python for Beginners"),
        ("Student 3", "student3@example.com", "Web Development with HTML/CSS"),
        ("Student 4", "student4@example.com", "APIs with Flask"),
        ("Student 5", "student5@example.com", "Intro to Data Science"),
    ]

    conn = get_db_connection()

    # Count how many students already exist in the database
    existing_students_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[
        0
    ]

    # Select the next student using modulo to loop the list
    next_student = sample_students[existing_students_count % len(sample_students)]

    # Insert the selected student into the database
    conn.execute(
        "INSERT INTO students (name, email, course) VALUES (?, ?, ?)", next_student
    )

    conn.commit()
    conn.close()

    # Simple response with a link back to home
    return 'Sample student added! <a href="/">Go back to home</a>'


if __name__ == "__main__":
    # Ensure the database and table exist before running the app
    init_db()

    # Start the Flask development server
    app.run(debug=True)
