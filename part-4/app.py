"""Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You will Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_demo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =============================================================================
# GLOBAL ERROR HANDLERS
# =============================================================================


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors globally."""
    return jsonify({"success": False, "error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors globally."""
    db.session.rollback()  # Rollback any failed transactions
    return jsonify({"success": False, "error": "Internal server error"}), 500


@app.errorhandler(400)
def bad_request_error(error):
    """Handle 400 errors globally."""
    return jsonify({"success": False, "error": "Bad request"}), 400


# =============================================================================
# MODELS
# =============================================================================


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Foreign Key (Many Books → One Author)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def to_dict(self):
        """Convert Book model to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "isbn": self.isbn,
            "author": {"id": self.author_ref.id, "name": self.author_ref.name},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    city = db.Column(db.String(100), nullable=False)

    # One-to-Many relationship
    books = db.relationship(
        "Book", backref="author_ref", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_books=True):
        """Convert Author model to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
        }
        if include_books:
            result["books"] = [book.to_dict() for book in self.books]
        return result


# =============================================================================
# REST API ROUTES FOR BOOK
# =============================================================================


# GET /api/books - Get all books
@app.route("/api/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify({
        "success": True,
        "count": len(books),
        "books": [book.to_dict() for book in books],
    })


# GET /api/books/<id> - Get single book
@app.route("/api/books/<int:id>", methods=["GET"])
def get_book(id):
    book = db.session.get(Book, id)  # Modern SQLAlchemy 2.0 syntax

    if not book:
        return jsonify({"success": False, "error": "Book not found"}), 404

    return jsonify({"success": True, "book": book.to_dict()})


# POST /api/books - Create new book
@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    if not data.get("title") or not data.get("author_id"):
        return jsonify({"success": False, "error": "Title and author_id are required"}), 400

    author = db.session.get(Author, data["author_id"])
    if not author:
        return jsonify({"success": False, "error": "Author not found"}), 404

    # Check for duplicate ISBN
    if data.get("isbn"):
        existing = Book.query.filter_by(isbn=data["isbn"]).first()
        if existing:
            return jsonify({"success": False, "error": "ISBN already exists"}), 400

    # Create book
    new_book = Book(
        title=data["title"],
        year=data.get("year"),
        isbn=data.get("isbn"),
        author_id=data["author_id"],
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book created successfully",
        "book": new_book.to_dict(),
    }), 201


# PUT /api/books/<id> - Update book
@app.route("/api/books/<int:id>", methods=["PUT"])
def update_book(id):
    book = db.session.get(Book, id)

    if not book:
        return jsonify({"success": False, "error": "Book not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    # Update fields if provided
    if "title" in data:
        book.title = data["title"]
    if "author_id" in data:
        # Validate author exists before updating
        if not db.session.get(Author, data["author_id"]):
            return jsonify({"success": False, "error": "Author not found"}), 404
        book.author_id = data["author_id"]
    if "year" in data:
        book.year = data["year"]
    if "isbn" in data:
        book.isbn = data["isbn"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Book updated successfully",
        "book": book.to_dict(),
    })


# DELETE /api/books/<id> - Delete book
@app.route("/api/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = db.session.get(Book, id)

    if not book:
        return jsonify({"success": False, "error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({"success": True, "message": "Book deleted successfully"})


# =============================================================================
# REST API ROUTES FOR AUTHOR
# =============================================================================


# GET /api/authors - Get all authors
@app.route("/api/authors", methods=["GET"])
def get_authors():
    authors = Author.query.all()
    return jsonify({
        "success": True,
        "count": len(authors),
        "authors": [author.to_dict() for author in authors],
    })


# GET /api/authors/<id> - Get single author
@app.route("/api/authors/<int:id>", methods=["GET"])
def get_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({"success": False, "error": "Author not found"}), 404

    return jsonify({"success": True, "author": author.to_dict()})


# POST /api/authors - Create new author
@app.route("/api/authors", methods=["POST"])
def create_author():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    if not data.get("name") or not data.get("city"):
        return jsonify({"success": False, "error": "Name and city are required"}), 400

    # Check duplicate author
    existing = Author.query.filter_by(name=data["name"]).first()
    if existing:
        return jsonify({"success": False, "error": "Author already exists"}), 400

    new_author = Author(name=data["name"], city=data["city"])

    db.session.add(new_author)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Author created successfully",
        "author": new_author.to_dict(),
    }), 201


# PUT /api/authors/<id> - Update author
@app.route("/api/authors/<int:id>", methods=["PUT"])
def update_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({"success": False, "error": "Author not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    # Update fields if provided
    if "name" in data:
        author.name = data["name"]
    if "city" in data:
        author.city = data["city"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Author updated successfully",
        "author": author.to_dict(),
    })


# DELETE /api/authors/<id> - Delete author
@app.route("/api/authors/<int:id>", methods=["DELETE"])
def delete_author(id):
    author = db.session.get(Author, id)

    if not author:
        return jsonify({"success": False, "error": "Author not found"}), 404

    db.session.delete(author)
    db.session.commit()

    return jsonify({"success": True, "message": "Author deleted successfully"})


# =============================================================================
# BONUS: Search and Filter
# =============================================================================


# GET /api/books/search?q=python&author=john
@app.route("/api/books/search", methods=["GET"])
def search_books():
    query = Book.query

    # Filter by title (partial match)
    title = request.args.get("q")
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    # Filter by author
    author = request.args.get("author")
    if author:
        query = query.join(Author).filter(Author.name.ilike(f"%{author}%"))

    # Filter by year
    year = request.args.get("year", type=int)
    if year:
        query = query.filter_by(year=year)

    books = query.all()

    return jsonify({
        "success": True,
        "count": len(books),
        "books": [book.to_dict() for book in books],
    })


# =============================================================================
# ADD PAGINATION
# =============================================================================
@app.route("/api/books/paginated", methods=["GET"])
def get_books_paginated():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)

    pagination = Book.query.order_by(Book.id.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "success": True,
        "page": page,
        "per_page": per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
        "books": [book.to_dict() for book in pagination.items],
    })


# =============================================================================
# ADD SORTING
# =============================================================================
@app.route("/api/books/sorted", methods=["GET"])
def get_books_sorted():
    sort_field = request.args.get("sort", default="id")
    order = request.args.get("order", default="asc")

    # Allowed columns for sorting (whitelist approach for security)
    allowed_sorts = {
        "id": Book.id,
        "title": Book.title,
        "year": Book.year,
        "isbn": Book.isbn,
        "created_at": Book.created_at,
    }

    sort_column = allowed_sorts.get(sort_field, Book.id)

    if order.lower() == "desc":
        query = Book.query.order_by(sort_column.desc())
    else:
        query = Book.query.order_by(sort_column.asc())

    books = query.all()

    return jsonify({
        "success": True,
        "sort": sort_field,
        "order": order,
        "count": len(books),
        "books": [book.to_dict() for book in books],
    })


# =============================================================================
# SIMPLE WEB PAGE FOR TESTING
# =============================================================================


@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>REST API Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            margin: 0;
        }

        .container {
            max-width: 1100px;
            margin: 40px auto;
            padding: 20px;
        }

        h1 { color: #38bdf8; }
        h2 { margin-top: 40px; color: #f472b6; }

        .card {
            background: #020617;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid #38bdf8;
        }

        .row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .method {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }

        .get { background: #16a34a; }
        .post { background: #f59e0b; }
        .put { background: #2563eb; }
        .delete { background: #dc2626; }

        code {
            background: #1e293b;
            padding: 3px 6px;
            border-radius: 4px;
        }

        input {
            padding: 8px;
            border-radius: 4px;
            border: none;
            background: #1e293b;
            color: #e5e7eb;
        }

        button {
            background: #38bdf8;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }

        button:hover { background: #0ea5e9; }

        pre {
            background: #020617;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-top: 20px;
            border-left: 4px solid #f472b6;
        }

        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: #94a3b8;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>📘 REST API Playground</h1>
    <p>Click <strong>Try it</strong> to call each endpoint using JavaScript fetch().</p>

    <h2>Books</h2>

    <div class="card">
        <span class="method get">GET</span>
        <code>/api/books</code>
        <div class="row">
            <button onclick="callApi('/api/books')">Try it</button>
        </div>
    </div>

    <div class="card">
        <span class="method get">GET</span>
        <code>/api/books/&lt;id&gt;</code>
        <div class="row">
            <input id="bookId" placeholder="Book ID">
            <button onclick="callApi('/api/books/' + bookId.value)">Try it</button>
        </div>
    </div>

    <div class="card">
        <span class="method get">GET</span>
        <code>/api/books/search?q=python</code>
        <div class="row">
            <input id="searchTitle" placeholder="Title keyword">
            <button onclick="callApi('/api/books/search?q=' + searchTitle.value)">Try it</button>
        </div>
    </div>

    <h2>Authors</h2>

    <div class="card">
        <span class="method get">GET</span>
        <code>/api/authors</code>
        <div class="row">
            <button onclick="callApi('/api/authors')">Try it</button>
        </div>
    </div>

    <div class="card">
        <span class="method get">GET</span>
        <code>/api/authors/&lt;id&gt;</code>
        <div class="row">
            <input id="authorId" placeholder="Author ID">
            <button onclick="callApi('/api/authors/' + authorId.value)">Try it</button>
        </div>
    </div>

    <h2>Response</h2>
    <pre id="output">Click a "Try it" button to see the response here.</pre>

    <div class="footer">
        This is a learning UI. Use Postman or curl for POST, PUT, DELETE.
    </div>
</div>

<script>
function callApi(url) {
    document.getElementById('output').textContent = 'Loading...';

    fetch(url)
        .then(res => res.json())
        .then(data => {
            document.getElementById('output').textContent =
                JSON.stringify(data, null, 2);
        })
        .catch(err => {
            document.getElementById('output').textContent = 'Error: ' + err;
        });
}
</script>

</body>
</html>
"""


# =============================================================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# =============================================================================


def init_db():
    with app.app_context():
        db.create_all()

        if Author.query.count() == 0:
            authors = [
                Author(name="Eric Matthes", city="New York"),
                Author(name="Miguel Grinberg", city="Washington"),
                Author(name="Robert C. Martin", city="London"),
            ]
            db.session.add_all(authors)
            db.session.commit()
            print("Sample authors added!")

        if Book.query.count() == 0:
            eric = Author.query.filter_by(name="Eric Matthes").first()
            miguel = Author.query.filter_by(name="Miguel Grinberg").first()
            robert = Author.query.filter_by(name="Robert C. Martin").first()

            books = [
                Book(
                    title="Python Crash Course",
                    year=2019,
                    isbn="978-1593279288",
                    author_id=eric.id,
                ),
                Book(
                    title="Flask Web Development",
                    year=2018,
                    isbn="978-1491991732",
                    author_id=miguel.id,
                ),
                Book(
                    title="Clean Code",
                    year=2008,
                    isbn="978-0132350884",
                    author_id=robert.id,
                ),
            ]

            db.session.add_all(books)
            db.session.commit()
            print("Sample books added!")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add pagination: `/api/books?page=1&per_page=10`
# 2. Add sorting: `/api/books?sort=title&order=desc`
# 3. Create a simple frontend using JavaScript fetch()
#
# =============================================================================
