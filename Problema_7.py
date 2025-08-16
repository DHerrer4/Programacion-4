import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

DB_NAME = "biblioteca.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS libros
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         titulo
                         TEXT
                         NOT
                         NULL,
                         autor
                         TEXT
                         NOT
                         NULL,
                         genero
                         TEXT
                         NOT
                         NULL,
                         estado
                         TEXT
                         NOT
                         NULL
                     )
                     """)


init_db()


@app.route("/")
def index():
    with sqlite3.connect(DB_NAME) as conn:
        libros = conn.execute("SELECT * FROM libros").fetchall()
    return render_template("index.html", libros=libros)


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        estado = request.form["estado"]

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO libros (titulo, autor, genero, estado) VALUES (?, ?, ?, ?)",
                         (titulo, autor, genero, estado))
        flash("Libro agregado correctamente", "success")
        return redirect(url_for("index"))

    return render_template("form_new.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    with sqlite3.connect(DB_NAME) as conn:
        libro = conn.execute("SELECT * FROM libros WHERE id = ?", (id,)).fetchone()

    if request.method == "POST":
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        estado = request.form["estado"]

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""UPDATE libros
                            SET titulo=?,
                                autor=?,
                                genero=?,
                                estado=?
                            WHERE id = ?""",
                         (titulo, autor, genero, estado, id))
        flash("Libro actualizado correctamente", "info")
        return redirect(url_for("index"))

    return render_template("form_edit.html", libro=libro)


@app.route("/eliminar/<int:id>", methods=["GET", "POST"])
def eliminar(id):
    if request.method == "POST":
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM libros WHERE id = ?", (id,))
        flash("Libro eliminado", "danger")
        return redirect(url_for("index"))

    return render_template("confirm_delete.html", id=id)


@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    if request.method == "POST":
        criterio = request.form["criterio"]
        termino = f"%{request.form['termino']}%"
        query = f"SELECT * FROM libros WHERE {criterio} LIKE ?"

        with sqlite3.connect(DB_NAME) as conn:
            resultados = conn.execute(query, (termino,)).fetchall()

        return render_template("search_results.html", resultados=resultados)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
