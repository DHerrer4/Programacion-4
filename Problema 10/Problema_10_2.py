from flask import Flask, jsonify, request
from db import add_book, get_book, update_book, delete_book

app = Flask(__name__)

@app.route("/books", methods=["GET"])
def list_books():
    from db import books_db
    return jsonify(books_db), 200

@app.route("/books/<int:book_id>", methods=["GET"])
def get_single_book(book_id):
    book = get_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
    data = request.json
    if not data or "title" not in data or "author" not in data:
        return jsonify({"error": "Invalid data"}), 400
    book = add_book(data)
    return jsonify(book), 201

@app.route("/books/<int:book_id>", methods=["PUT"])
def edit_book(book_id):
    data = request.json
    book = update_book(book_id, data)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

@app.route("/books/<int:book_id>", methods=["DELETE"])
def remove_book(book_id):
    book = delete_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
