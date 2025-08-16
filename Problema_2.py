import sqlite3

# ==========================
# CONEXIÓN A LA BASE DE DATOS
# ==========================
def conectar():
    return sqlite3.connect("biblioteca.db")

# ==========================
# CREACIÓN DE TABLA
# ==========================
def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        genero TEXT NOT NULL,
        estado_lectura TEXT NOT NULL CHECK(estado_lectura IN ('Leído', 'No leído'))
    );
    """)
    conn.commit()
    conn.close()

# ==========================
# FUNCIONES CRUD
# ==========================
def agregar_libro():
    titulo = input("📖 Título: ")
    autor = input("✍ Autor: ")
    genero = input("🏷 Género: ")
    estado = input("✅ Estado de lectura (Leído/No leído): ")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO libros (titulo, autor, genero, estado_lectura) VALUES (?, ?, ?, ?)",
                   (titulo, autor, genero, estado))
    conn.commit()
    conn.close()
    print("✅ Libro agregado correctamente.")

def actualizar_libro():
    ver_libros()
    try:
        id_libro = int(input("ID del libro a actualizar: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    titulo = input("📖 Nuevo título: ")
    autor = input("✍ Nuevo autor: ")
    genero = input("🏷 Nuevo género: ")
    estado = input("✅ Nuevo estado de lectura (Leído/No leído): ")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE libros
        SET titulo=?, autor=?, genero=?, estado_lectura=?
        WHERE id=?
    """, (titulo, autor, genero, estado, id_libro))
    conn.commit()
    conn.close()
    print("✅ Libro actualizado correctamente.")

def eliminar_libro():
    ver_libros()
    try:
        id_libro = int(input("ID del libro a eliminar: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM libros WHERE id=?", (id_libro,))
    conn.commit()
    conn.close()
    print("🗑 Libro eliminado correctamente.")

def ver_libros():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    conn.close()

    print("\n📚 LISTA DE LIBROS")
    print("-" * 60)
    for libro in libros:
        print(f"ID: {libro[0]} | Título: {libro[1]} | Autor: {libro[2]} | Género: {libro[3]} | Estado: {libro[4]}")
    print("-" * 60)

def buscar_libros():
    print("\n🔍 Buscar por:")
    print("1. Título")
    print("2. Autor")
    print("3. Género")
    opcion = input("Seleccione opción: ")

    campo = None
    if opcion == "1":
        campo = "titulo"
    elif opcion == "2":
        campo = "autor"
    elif opcion == "3":
        campo = "genero"
    else:
        print("❌ Opción inválida.")
        return

    valor = input(f"Ingrese {campo}: ")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM libros WHERE {campo} LIKE ?", ('%' + valor + '%',))
    resultados = cursor.fetchall()
    conn.close()

    if resultados:
        print("\n📌 RESULTADOS DE LA BÚSQUEDA:")
        for libro in resultados:
            print(f"ID: {libro[0]} | Título: {libro[1]} | Autor: {libro[2]} | Género: {libro[3]} | Estado: {libro[4]}")
    else:
        print("⚠ No se encontraron libros.")

# ==========================
# MENÚ PRINCIPAL
# ==========================
def menu():
    crear_tabla()
    while True:
        print("\n====== 📚 BIBLIOTECA PERSONAL ======")
        print("1. Agregar nuevo libro")
        print("2. Actualizar información de un libro")
        print("3. Eliminar libro existente")
        print("4. Ver listado de libros")
        print("5. Buscar libros")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

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
            print("❌ Opción inválida.")

# ==========================
# EJECUCIÓN
# ==========================
if __name__ == "__main__":
    menu()
