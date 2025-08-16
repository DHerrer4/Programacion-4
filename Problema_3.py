from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum


# ==========================
# ENUM PARA ESTADO DE LECTURA
# ==========================
class EstadoLectura(enum.Enum):
    LEIDO = "Leído"
    NO_LEIDO = "No leído"


# ==========================
# CONFIGURACIÓN BASE ORM
# ==========================
Base = declarative_base()


class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    genero = Column(String(100), nullable=False)
    estado_lectura = Column(Enum(EstadoLectura), nullable=False)


# ==========================
# CONEXIÓN A MARIADB
# ==========================
def get_engine():
    """
    Cambia los valores según tu configuración de MariaDB:
    usuario: root
    contraseña: tu_password
    host: localhost
    base_de_datos: biblioteca
    """
    USER = "root"
    PASSWORD = "tu_password"
    HOST = "localhost"
    DB_NAME = "biblioteca"

    try:
        engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}")
        return engine
    except Exception as e:
        print("❌ Error al conectar a la base de datos:", e)
        exit()


# ==========================
# OPERACIONES CRUD
# ==========================
def agregar_libro(session):
    titulo = input("📖 Título: ")
    autor = input("✍ Autor: ")
    genero = input("🏷 Género: ")

    while True:
        estado = input("✅ Estado (Leído/No leído): ")
        if estado in ["Leído", "No leído"]:
            break
        print("⚠ Valor inválido, intente nuevamente.")

    libro = Libro(
        titulo=titulo,
        autor=autor,
        genero=genero,
        estado_lectura=EstadoLectura.LEIDO if estado == "Leído" else EstadoLectura.NO_LEIDO
    )
    session.add(libro)
    session.commit()
    print("✅ Libro agregado correctamente.")


def actualizar_libro(session):
    ver_libros(session)
    try:
        id_libro = int(input("ID del libro a actualizar: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    libro = session.query(Libro).filter_by(id=id_libro).first()
    if not libro:
        print("⚠ Libro no encontrado.")
        return

    libro.titulo = input(f"📖 Nuevo título ({libro.titulo}): ") or libro.titulo
    libro.autor = input(f"✍ Nuevo autor ({libro.autor}): ") or libro.autor
    libro.genero = input(f"🏷 Nuevo género ({libro.genero}): ") or libro.genero

    while True:
        estado = input(
            f"✅ Nuevo estado ({libro.estado_lectura.value}) [Leído/No leído]: ") or libro.estado_lectura.value
        if estado in ["Leído", "No leído"]:
            libro.estado_lectura = EstadoLectura.LEIDO if estado == "Leído" else EstadoLectura.NO_LEIDO
            break
        print("⚠ Valor inválido.")

    session.commit()
    print("✅ Libro actualizado.")


def eliminar_libro(session):
    ver_libros(session)
    try:
        id_libro = int(input("ID del libro a eliminar: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    libro = session.query(Libro).filter_by(id=id_libro).first()
    if libro:
        session.delete(libro)
        session.commit()
        print("🗑 Libro eliminado.")
    else:
        print("⚠ Libro no encontrado.")


def ver_libros(session):
    libros = session.query(Libro).all()
    print("\n📚 LISTADO DE LIBROS")
    print("-" * 60)
    for libro in libros:
        print(f"ID: {libro.id} | {libro.titulo} | {libro.autor} | {libro.genero} | {libro.estado_lectura.value}")
    print("-" * 60)


def buscar_libros(session):
    print("\n🔍 Buscar por:")
    print("1. Título")
    print("2. Autor")
    print("3. Género")
    opcion = input("Seleccione opción: ")

    campo = None
    if opcion == "1":
        campo = Libro.titulo
    elif opcion == "2":
        campo = Libro.autor
    elif opcion == "3":
        campo = Libro.genero
    else:
        print("❌ Opción inválida.")
        return

    valor = input("Ingrese búsqueda: ")
    resultados = session.query(Libro).filter(campo.like(f"%{valor}%")).all()

    if resultados:
        for libro in resultados:
            print(f"ID: {libro.id} | {libro.titulo} | {libro.autor} | {libro.genero} | {libro.estado_lectura.value}")
    else:
        print("⚠ No se encontraron coincidencias.")


# ==========================
# MENÚ PRINCIPAL
# ==========================
def menu():
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    while True:
        print("\n====== 📚 BIBLIOTECA PERSONAL (MariaDB + SQLAlchemy) ======")
        print("1. Agregar nuevo libro")
        print("2. Actualizar libro")
        print("3. Eliminar libro")
        print("4. Ver libros")
        print("5. Buscar libros")
        print("6. Salir")
        opcion = input("Seleccione: ")

        if opcion == "1":
            agregar_libro(session)
        elif opcion == "2":
            actualizar_libro(session)
        elif opcion == "3":
            eliminar_libro(session)
        elif opcion == "4":
            ver_libros(session)
        elif opcion == "5":
            buscar_libros(session)
        elif opcion == "6":
            print("👋 Saliendo...")
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu()
