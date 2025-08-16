from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import json
import uuid
from config import settings
from extensions import mail
from celery_app import celery
from tasks import send_email_task

ALLOWED_ESTADOS = {"Leído", "No leído", "Pendiente"}


# ---------- Helpers ----------

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


def scan_books(r):
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
    return sorted(books, key=lambda x: x.get("titulo", "").lower())


# ---------- App Factory ----------

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_USE_TLS=settings.MAIL_USE_TLS,
        MAIL_USE_SSL=settings.MAIL_USE_SSL,
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_DEFAULT_SENDER=settings.MAIL_DEFAULT_SENDER,
    )

    # Extensiones
    mail.init_app(app)

    # KeyDB client
    app.keydb = redis.Redis(
        host=settings.KEYDB_HOST,
        port=settings.KEYDB_PORT,
        password=settings.KEYDB_PASSWORD,
        decode_responses=True,
    )

    # Rutas
    register_routes(app)

    # Celery: asegurar contexto de app en tareas render_template/mail
    # (Patrón simple: envolver task execution con app_context en worker)
    # Ver README para comando de arranque del worker.

    return app


def register_routes(app: Flask):
    @app.route("/")
    def index():
        campo = request.args.get("campo", "titulo")
        q = request.args.get("q", "").lower().strip()
        libros = scan_books(app.keydb)
        if q and campo in {"titulo", "autor", "genero"}:
            libros = [b for b in libros if q in str(b.get(campo, "")).lower()]
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

            # Evitar duplicados por título (opcional)
            for b in scan_books(app.keydb):
                if b.get("titulo", "").lower() == titulo.lower():
                    flash("Ya existe un libro con ese título.", "warning")
                    return render_template("form_new.html", form=request.form)

            book_id = str(uuid.uuid4())
            doc = {"id": book_id, "titulo": titulo, "autor": autor, "genero": genero, "estado": estado}
            app.keydb.set(_key(book_id), json.dumps(doc))

            flash("Libro agregado correctamente.", "success")

            # Disparar correo asíncrono
            if settings.NOTIFY_EMAIL:
                send_email_task.delay(
                    subject="[Biblioteca] Nuevo libro agregado",
                    recipient=settings.NOTIFY_EMAIL,
                    template_name="email/added.html",
                    context={"libro": doc},
                )
            return redirect(url_for("index"))

        return render_template("form_new.html", form={})

    @app.route("/editar/<book_id>", methods=["GET", "POST"])
    def editar(book_id):
        raw = app.keydb.get(_key(book_id))
        if not raw:
            flash("Libro no encontrado.", "warning")
            return redirect(url_for("index"))
        doc = json.loads(raw)

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            autor = request.form.get("autor", "").strip()
            genero = request.form.get("genero", "").strip()
            estado = request.form.get("estado", "").strip()

            errors = _validate_payload(titulo, autor, genero, estado)
            if errors:
                for e in errors: flash(e, "danger")
                return render_template("form_edit.html", form=request.form, book_id=book_id)

            # Verifica duplicados de título
            if titulo.lower() != doc["titulo"].lower():
                for b in scan_books(app.keydb):
                    if b["id"] != book_id and b.get("titulo", "").lower() == titulo.lower():
                        flash("Ya existe otro libro con ese título.", "warning")
                        return render_template("form_edit.html", form=request.form, book_id=book_id)

            doc.update({"titulo": titulo, "autor": autor, "genero": genero, "estado": estado})
            app.keydb.set(_key(book_id), json.dumps(doc))
            flash("Libro actualizado correctamente.", "info")
            return redirect(url_for("index"))

        return render_template("form_edit.html", form=doc, book_id=book_id)

    @app.route("/eliminar/<book_id>", methods=["GET", "POST"])
    def eliminar(book_id):
        raw = app.keydb.get(_key(book_id))
        if not raw:
            flash("Libro no encontrado.", "warning")
