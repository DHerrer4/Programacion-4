books_db = []
next_id = 1

def add_book(book_data):
    global next_id
    book = {
        "id": next_id,
        "title": book_data["title"],
        "author": book_data["author"],
        "genre": book_data["genre"],
        "read": book_data.get("read", False)
    }
    books_db.append(book)
    next_id += 1
    return book

def get_book(book_id):
    return next((b for b in books_db if b["id"] == book_id), None)

def update_book(book_id, data):
    book = get_book(book_id)
    if book:
        book.update(data)
    return book

def delete_book(book_id):
    global books_db
    book = get_book(book_id)
    if book:
        books_db = [b for b in books_db if b["id"] != book_id]
    return book
