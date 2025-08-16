import redis
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conexión a KeyDB
try:
    r = redis.Redis(
        host=os.getenv("KEYDB_HOST", "localhost"),
        port=int(os.getenv("KEYDB_PORT", 6379)),
        password=os.getenv("KEYDB_PASSWORD", None),
        decode_responses=True
    )
    r.ping()
    print("✅ Conectado a KeyDB correctamente.")
except redis.ConnectionError as e:
    print("❌ Error al conectar a KeyDB:", e)
    exit()

# Funciones CRUD
def agregar_libro():
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    genero = input("Género: ").strip()
    estado = input("Estado de lectura (Leído / Pendiente): ").strip()

    key = f"libro:{titulo.lower().replace(' ', '_')}"
    if r.exists(key):
        print("⚠ Ya existe un libro con ese título.")
        return

    libro = {
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "estado": estado
    }
    r.set(key, json.dumps(libro))
    print("📚 Libro agregado con éxito.")

def actualizar_libro():
    titulo = input("Título del libro a actualizar: ").strip()
    key = f"libro:{titulo.lower().replace(' ', '_')}"

    if not r.exists(key):
        print("⚠ No se encontró el libro.")
        return

    libro = json.loads(r.get(key))

    print("Deja en blanco si no quieres cambiar un campo.")
    nuevo_autor = input(f"Autor ({libro['autor']}): ").strip()
    nuevo_genero = input(f"Género ({libro['genero']}): ").strip()
    nuevo_estado = input(f"Estado ({libro['estado']}): ").strip()

    if nuevo_autor:
        libro["autor"] = nuevo_autor
    if nuevo_genero:
        libro["genero"] = nuevo_genero
    if nuevo_estado:
        libro["estado"] = nuevo_estado

    r.set(key, json.dumps(libro))
    print("✏ Libro actualizado correctamente.")

def eliminar_libro():
    titulo = input("Título del libro a eliminar: ").strip()
    key = f"libro:{titulo.lower().replace(' ', '_')}"
    if r.delete(key):
        print("🗑 Libro eliminado correctamente.")
    else:
        print("⚠ No se encontró el libro.")

def ver_libros():
    keys = r.keys("libro:*")
    if not keys:
        print("📭 No hay libros registrados.")
        return

    for key in keys:
        libro = json.loads(r.get(key))
        print(f"📖 {libro['titulo']} - {libro['autor']} ({libro['genero']}) - Estado: {libro['estado']}")

def buscar_libros():
    criterio = input("Buscar por (titulo/autor/genero): ").strip().lower()
    valor = input("Valor a buscar: ").strip().lower()

    keys = r.keys("libro:*")
    encontrados = []

    for key in keys:
        libro = json.loads(r.get(key))
        if criterio in libro and valor in libro[criterio].lower():
            encontrados.append(libro)

    if encontrados:
        print("🔍 Resultados encontrados:")
        for libro in encontrados:
            print(f"📖 {libro['titulo']} - {libro['autor']} ({libro['genero']}) - Estado: {libro['estado']}")
    else:
        print("⚠ No se encontraron coincidencias.")

# Menú principal
def menu():
    while True:
        print("\n=== Biblioteca Personal (KeyDB) ===")
        print("1. Agregar libro")
        print("2. Actualizar libro")
        print("3. Eliminar libro")
        print("4. Ver todos los libros")
        print("5. Buscar libros")
        print("6. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            agregar_libro()
        elif opcion == "2":
            actualizar_libro()
        elif opcion == "3":
            eliminar_libro()
        elif opcion == "4":
            ver_libros()
        elif opcion == "5":
            buscar_libros()
        elif opcion == "6":
            print("👋 Saliendo del programa...")
            break
        else:
            print("❌ Opción no válida.")

if __name__ == "__main__":
    menu()
