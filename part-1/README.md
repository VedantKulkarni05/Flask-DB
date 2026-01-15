# Part 1: Flask + SQLite (Create & Read)

## Overview

A simple Flask application that connects to an SQLite database and displays student data.  
This part focuses on moving from hardcoded data to a real database.

## What You'll Learn

- Connecting a Flask app to an SQLite database
- Creating a database table using SQL
- Inserting records into the database (CREATE)
- Reading records from the database (READ)
- Displaying database data in a Jinja template

## Prerequisites

- Basic understanding of Flask
  - Routes
  - Templates
  - `render_template`
- Completion of a basic Flask introduction

## How to Run the App

```bash
# Navigate to the project folder
cd part-1

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install flask

# Start the Flask app
python app.py
```

## How to Test It

Open your browser and go to `http://localhost:5000`

You will see an empty student table

Click "Add Sample Student"

Refresh the page to see the student added to the database

## Project Structure

```
part-1/
├── app.py              # Flask app and database logic
├── templates/
│   └── index.html      # Student list page
├── students.db         # SQLite database (auto-created)
└── README.md           # Project documentation
```

## Key Concepts Explained

| Concept | Purpose |
|---------|---------|
| sqlite3.connect() | Opens a connection to the database file |
| CREATE TABLE | Defines the database structure |
| INSERT INTO | Adds new data to the table |
| SELECT * FROM | Reads all records from the table |
| commit() | Saves database changes |
| close() | Releases the database connection |
| fetchall() | Retrieves all rows from a query result |
