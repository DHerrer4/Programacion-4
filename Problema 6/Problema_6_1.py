from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import json
import uuid
from config import settings

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

# Conexión global a KeyDB
r = redis.Redis(
    host=settings.KEYDB_HOST,
    port=settings.KEYDB_PORT,
    password=settings.KEYDB_PASSWORD,
    decode_responses=True,
)

ALLOWED_ESTADOS = {"Leído", "No leído", "Pendiente"}

# --- Helpers ---

def _key(book_id: str) -> str:
    return f"{settings.PREFIX}{book_id}"


def _validate_payload(titulo, autor, genero, estado):
    errors = []
    if not titulo: errors.append("El título es obligatorio.")
    if not autor: errors.append("El autor es obligatorio.")
    if not genero: errors.append("El género es obligatorio.")
    if estado not in ALLOWED_ESTADOS:
        errors.append("Estado inválido. Usa 'Leído', 'No leído' o 'Pendiente'.")
    return errors


def get_book(book_id: str):
    data = r.get(_key(book_id))
    return json.loads(data) if data else None


def save_book(doc: dict):
    # doc debe contener un campo 'id'
    r.set(_key(doc["id"]), json.dumps(doc))


def delete_book(book_id: str):
    r.delete(_key(book_id))


def scan_books():
    """Devuelve todos los libros como lista de dicts usando SCAN."""
    cursor = 0
    books = []
    while True:
        cursor, keys = r.scan(cursor=cursor, match=settings.SCAN_PATTERN, count=200)
        if keys:
            values = r.mget(keys)
            for raw in values:
                if raw:
                    books.append(json.loads(raw))
        if cursor == 0:
            break
    # Ordenar por título para visual consistente
    return sorted(books, key=lambda x: x.get("titulo", "").lower())


def find_books_by(field: str, query: str):
    query = (query or "").strip().lower()
    if not query:
        return scan_books()
    field = field if field in {"titulo", "autor", "genero"} else "titulo"
    results = []
    for doc in scan_books():
        val = str(doc.get(field, "")).lower()
        if query in val:
            results.append(doc)
    return results

# --- Rutas ---

@app.route("/")
def index():
    campo = request.args.get("campo", "titulo")
    q = request.args.get("q", "")
    libros = find_books_by(campo, q)
    return render_template("index.html", libros=libros, campo=campo, q=q)


@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        estado = request.form.get("estado", "").strip()

        errors = _validate_payload(titulo, autor, genero, estado)
        if errors:
            for e in errors: flash(e, "danger")
            return render_template("form_new.html", form=request.form)

        # Evitar duplicados exactos por título (opcional y simple)
        for doc in scan_books():
            if doc.get("titulo", "").strip().lower() == titulo.lower():
                flash("Ya existe un libro con ese título.", "warning")
                return render_template("form_new.html", form=request.form)

        book_id = str(uuid.uuid4())
        doc = {
            "id": book_id,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado,
        }
        save_book(doc)
        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("form_new.html", form={})


@app.route("/editar/<book_id>", methods=["GET", "POST"])
def editar(book_id):
    doc = get_book(book_id)
    if not doc:
        flash("Libro no encontrado.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        estado = request.form.get("estado", "").strip()

        errors = _validate_payload(titulo, autor, genero, estado)
        if errors:
            for e in errors: flash(e, "danger")
            return render_template("form_edit.html", form=request.form, book_id=book_id)

        # Si cambia el título, verifica duplicados (excepto el propio)
        if titulo.lower() != doc["titulo"].lower():
            for other in scan_books():
                if other["id"] != book_id and other.get("titulo", "").lower() == titulo.lower():
                    flash("Ya existe otro libro con ese título.", "warning")
                    return render_template("form_edit.html", form=request.form, book_id=book_id)

        doc.update({
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado,
        })
        save_book(doc)
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("index"))

    # GET
    return render_template("form_edit.html", form=doc, book_id=book_id)


@app.route("/eliminar/<book_id>", methods=["POST"])
def eliminar(book_id):
    if not get_book(book_id):
        flash("Libro no encontrado.", "warning")
    else:
        delete_book(book_id)
        flash("Libro eliminado.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Ejecuta: flask --app app.py --debug run  (o python app.py)
    app.run(debug=True)