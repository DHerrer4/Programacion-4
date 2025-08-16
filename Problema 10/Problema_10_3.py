from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def index():
    try:
        resp = requests.get(f"{API_URL}/books")
        books = resp.json() if resp.status_code == 200 else []
    except:
        flash("Error al conectar con la API")
        books = []
    return render_template("index.html", books=books)

@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "author": request.form["author"],
            "genre": request.form["genre"],
            "read": "read" in request.form
        }
        resp = requests.post(f"{API_URL}/books", json=data)
        if resp.status_code == 201:
            flash("Libro agregado correctamente")
            return redirect(url_for("index"))
        else:
            flash("Error al agregar libro")
    return render_template("add.html")

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "author": request.form["author"],
            "genre": request.form["genre"],
            "read": "read" in request.form
        }
        resp = requests.put(f"{API_URL}/books/{book_id}", json=data)
        if resp.status_code == 200:
            flash("Libro actualizado")
            return redirect(url_for("index"))
        else:
            flash("Error al actualizar libro")
    else:
        resp = requests.get(f"{API_URL}/books/{book_id}")
        if resp.status_code != 200:
            flash("Libro no encontrado")
            return redirect(url_for("index"))
        book = resp.json()
        return render_template("edit.html", book=book)

@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    resp = requests.delete(f"{API_URL}/books/{book_id}")
    if resp.status_code == 200:
        flash("Libro eliminado")
    else:
        flash("Error al eliminar libro")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
