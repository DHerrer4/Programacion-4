import sqlite3

# Conexión a la base de datos (en memoria para pruebas)
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# ==========================
# CREACIÓN DE TABLAS
# ==========================
cursor.execute("""
CREATE TABLE heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    clase TEXT NOT NULL CHECK(clase IN ('Guerrero', 'Mago', 'Arquero', 'Clérigo', 'Asesino', 'Bárbaro')),
    nivel_experiencia INTEGER NOT NULL CHECK(nivel_experiencia >= 1)
);
""")

cursor.execute("""
CREATE TABLE misiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dificultad INTEGER NOT NULL CHECK(dificultad BETWEEN 1 AND 10),
    localizacion TEXT NOT NULL,
    recompensa INTEGER NOT NULL CHECK(recompensa >= 0)
);
""")

cursor.execute("""
CREATE TABLE monstruos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('Dragón', 'Goblin', 'No-muerto', 'Bestia', 'Demonio', 'Elemental')),
    nivel_amenaza INTEGER NOT NULL CHECK(nivel_amenaza BETWEEN 1 AND 5)
);
""")

cursor.execute("""
CREATE TABLE misiones_heroes (
    id_mision INTEGER NOT NULL,
    id_hero INTEGER NOT NULL,
    PRIMARY KEY (id_mision, id_hero),
    FOREIGN KEY (id_mision) REFERENCES misiones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_hero) REFERENCES heroes(id) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE misiones_monstruos (
    id_mision INTEGER NOT NULL,
    id_monstruo INTEGER NOT NULL,
    PRIMARY KEY (id_mision, id_monstruo),
    FOREIGN KEY (id_mision) REFERENCES misiones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_monstruo) REFERENCES monstruos(id) ON DELETE CASCADE
);
""")

# ==========================
# INSERCIÓN DE DATOS DE EJEMPLO
# ==========================
heroes = [
    ("Arthas", "Guerrero", 15),
    ("Merlín", "Mago", 20),
    ("Legolas", "Arquero", 18),
    ("Lilith", "Asesino", 12)
]
cursor.executemany("INSERT INTO heroes (nombre, clase, nivel_experiencia) VALUES (?, ?, ?)", heroes)

misiones = [
    ("Defender el reino", 9, "Castillo Real", 500),
    ("Explorar la caverna oscura", 7, "Montañas Grises", 300),
    ("Cazar al dragón de fuego", 10, "Valle Ardiente", 1000)
]
cursor.executemany("INSERT INTO misiones (nombre, dificultad, localizacion, recompensa) VALUES (?, ?, ?, ?)", misiones)

monstruos = [
    ("Smaug", "Dragón", 5),
    ("Goblin Gruñón", "Goblin", 2),
    ("Esqueleto Maldito", "No-muerto", 3),
    ("Lobo Gigante", "Bestia", 4)
]
cursor.executemany("INSERT INTO monstruos (nombre, tipo, nivel_amenaza) VALUES (?, ?, ?)", monstruos)

# ==========================
# RELACIONES
# ==========================
misiones_heroes = [
    (1, 1),  # Arthas en Defender el reino
    (1, 2),  # Merlín en Defender el reino
    (2, 3),  # Legolas en Explorar la caverna oscura
    (2, 4),  # Lilith en Explorar la caverna oscura
    (3, 1),  # Arthas en Cazar al dragón de fuego
    (3, 3)   # Legolas en Cazar al dragón de fuego
]
cursor.executemany("INSERT INTO misiones_heroes VALUES (?, ?)", misiones_heroes)

misiones_monstruos = [
    (1, 2),  # Goblin en Defender el reino
    (1, 3),  # Esqueleto en Defender el reino
    (2, 4),  # Lobo gigante en Explorar caverna
    (3, 1)   # Dragón Smaug en Cazar al dragón de fuego
]
cursor.executemany("INSERT INTO misiones_monstruos VALUES (?, ?)", misiones_monstruos)

conn.commit()

# ==========================
# CONSULTA EJEMPLO
# ==========================
print("=== Héroes que enfrentaron un Dragón en misiones de dificultad ≥ 8 ===")
cursor.execute("""
SELECT DISTINCT h.nombre, m.nombre AS mision, mon.nombre AS dragon
FROM heroes h
JOIN misiones_heroes mh ON h.id = mh.id_hero
JOIN misiones m ON mh.id_mision = m.id
JOIN misiones_monstruos mm ON m.id = mm.id_mision
JOIN monstruos mon ON mm.id_monstruo = mon.id
WHERE mon.tipo = 'Dragón' AND m.dificultad >= 8;
""")
for fila in cursor.fetchall():
    print(f"{fila[0]} participó en '{fila[1]}' contra {fila[2]}")

# Cerrar conexión
conn.close()
