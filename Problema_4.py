from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys


# ========================
# CONFIGURACIÓN DE MONGODB
# ========================
def conectar_mongodb():
    try:
        # Cambia según tu configuración (usuario, contraseña, host, puerto, base de datos)
        uri = "mongodb://localhost:27017"
        cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
        cliente.admin.command("ping")  # Verifica conexión
        print("✅ Conexión exitosa a MongoDB.")
        return cliente["biblioteca"]  # Base de datos 'biblioteca'
    except ConnectionFailure:
        print("❌ No se pudo conectar a MongoDB. Verifica que el servidor esté en ejecución.")
        sys.exit(1)


# ========================
# FUNCIONES CRUD
# ========================
def agregar_libro(coleccion):
    titulo = input("Título: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    estado = input("Estado de lectura (pendiente/en progreso/finalizado): ")

    libro = {
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "estado": estado
    }

    coleccion.insert_one(libro)
    print("📚 Libro agregado con éxito.")


def actualizar_libro(coleccion):
    titulo = input("Ingrese el título del libro a actualizar: ")
    libro = coleccion.find_one({"titulo": titulo})

    if not libro:
        print("⚠ No se encontró un libro con ese título.")
        return

    print("Deja en blanco para no modificar un campo.")
    nuevo_titulo = input(f"Nuevo título [{libro['titulo']}]: ") or libro['titulo']
    nuevo_autor = input(f"Nuevo autor [{libro['autor']}]: ") or libro['autor']
    nuevo_genero = input(f"Nuevo género [{libro['genero']}]: ") or libro['genero']
    nuevo_estado = input(f"Nuevo estado [{libro['estado']}]: ") or libro['estado']

    coleccion.update_one(
        {"_id": libro["_id"]},
        {"$set": {
            "titulo": nuevo_titulo,
            "autor": nuevo_autor,
            "genero": nuevo_genero,
            "estado": nuevo_estado
        }}
    )
    print("✏ Libro actualizado correctamente.")


def eliminar_libro(coleccion):
    titulo = input("Ingrese el título del libro a eliminar: ")
    resultado = coleccion.delete_one({"titulo": titulo})

    if resultado.deleted_count > 0:
        print("🗑 Libro eliminado correctamente.")
    else:
        print("⚠ No se encontró un libro con ese título.")


def listar_libros(coleccion):
    libros = list(coleccion.find())

    if not libros:
        print("⚠ No hay libros registrados.")
        return

    print("\n📚 Listado de libros:")
    for libro in libros:
        print(f"- {libro['titulo']} | {libro['autor']} | {libro['genero']} | {libro['estado']}")


def buscar_libros(coleccion):
    criterio = input("Buscar por (titulo/autor/genero): ").lower()
    if criterio not in ["titulo", "autor", "genero"]:
        print("⚠ Criterio no válido.")
        return

    valor = input(f"Ingrese el {criterio} a buscar: ")
    resultados = list(coleccion.find({criterio: {"$regex": valor, "$options": "i"}}))

    if not resultados:
        print("⚠ No se encontraron resultados.")
        return

    print("\n🔍 Resultados de búsqueda:")
    for libro in resultados:
        print(f"- {libro['titulo']} | {libro['autor']} | {libro['genero']} | {libro['estado']}")


# ========================
# MENÚ PRINCIPAL
# ========================
def menu():
    db = conectar_mongodb()
    coleccion_libros = db["libros"]

    opciones = {
        "1": lambda: agregar_libro(coleccion_libros),
        "2": lambda: actualizar_libro(coleccion_libros),
        "3": lambda: eliminar_libro(coleccion_libros),
        "4": lambda: listar_libros(coleccion_libros),
        "5": lambda: buscar_libros(coleccion_libros),
        "6": lambda: salir()
    }

    while True:
        print("\n=== 📚 Biblioteca Personal ===")
        print("1. Agregar libro")
        print("2. Actualizar libro")
        print("3. Eliminar libro")
        print("4. Ver listado de libros")
        print("5. Buscar libros")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

        accion = opciones.get(opcion)
        if accion:
            accion()
        else:
            print("⚠ Opción no válida.")


def salir():
    print("👋 Saliendo de la aplicación...")
    sys.exit(0)


if __name__ == "__main__":
    menu()
