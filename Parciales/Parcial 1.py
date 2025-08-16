import sqlite3
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
from tabulate import tabulate

# Inicializar colorama
init(autoreset=True)


class BaseDatos:
    def __init__(self, nombre_db="presupuesto.db"):
        self.conn = sqlite3.connect(nombre_db)
        self.cursor = self.conn.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS articulos
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                nombre
                                TEXT
                                NOT
                                NULL,
                                categoria
                                TEXT
                                NOT
                                NULL,
                                cantidad
                                REAL
                                NOT
                                NULL,
                                precio_unitario
                                REAL
                                NOT
                                NULL,
                                descripcion
                                TEXT,
                                fecha
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            ''')

        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS gastos
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                descripcion
                                TEXT
                                NOT
                                NULL,
                                monto
                                REAL
                                NOT
                                NULL,
                                categoria
                                TEXT
                                NOT
                                NULL,
                                fecha
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            ''')
        self.conn.commit()

    def ejecutar(self, query, params=None):
        """Método genérico para ejecutar queries"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return self.cursor.fetchall() if query.strip().upper().startswith('SELECT') else self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"{Fore.RED}Error en base de datos: {e}")
            self.conn.rollback()
            return None

    def insertar_articulo(self, nombre, categoria, cantidad, precio, descripcion=""):
        return self.ejecutar(
            'INSERT INTO articulos (nombre, categoria, cantidad, precio_unitario, descripcion) VALUES (?, ?, ?, ?, ?)',
            (nombre, categoria, cantidad, precio, descripcion)
        )

    def obtener_articulos(self, filtro=None, valor=None):
        if filtro and valor:
            return self.ejecutar(f'SELECT * FROM articulos WHERE {filtro} LIKE ?', (f'%{valor}%',))
        return self.ejecutar('SELECT * FROM articulos ORDER BY categoria, nombre')

    def actualizar_articulo(self, id_articulo, nombre, categoria, cantidad, precio, descripcion):
        return self.ejecutar(
            'UPDATE articulos SET nombre=?, categoria=?, cantidad=?, precio_unitario=?, descripcion=? WHERE id=?',
            (nombre, categoria, cantidad, precio, descripcion, id_articulo)
        )

    def eliminar_articulo(self, id_articulo):
        return self.ejecutar('DELETE FROM articulos WHERE id=?', (id_articulo,))

    def insertar_gasto(self, descripcion, monto, categoria):
        return self.ejecutar(
            'INSERT INTO gastos (descripcion, monto, categoria) VALUES (?, ?, ?)',
            (descripcion, monto, categoria)
        )

    def obtener_gastos(self, categoria=None):
        if categoria:
            return self.ejecutar('SELECT * FROM gastos WHERE categoria=? ORDER BY fecha DESC', (categoria,))
        return self.ejecutar('SELECT * FROM gastos ORDER BY fecha DESC')

    def cerrar(self):
        if hasattr(self, 'conn'):
            self.conn.close()


class GestorPresupuesto:
    def __init__(self):
        self.db = BaseDatos()
        self.running = True

    def input_validado(self, mensaje, validador=None, error="Entrada inválida"):
        """Entrada con validación simplificada"""
        while True:
            valor = input(f"{Fore.WHITE}{mensaje}").strip()
            if not validador or validador(valor):
                return valor
            print(f"{Fore.RED}{error}")

    def mostrar_menu(self):
        opciones = [
            "Registrar artículo", "Buscar artículos", "Editar artículo",
            "Eliminar artículo", "Listar artículos", "Exportar a CSV",
            "Registrar gasto", "Ver gastos", "Visualizar gastos",
            "Reporte completo", "Salir"
        ]

        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{Style.BRIGHT}SISTEMA DE PRESUPUESTO")
        print(f"{'=' * 50}")

        for i, opcion in enumerate(opciones, 1):
            print(f"{Fore.YELLOW}{i}. {opcion}")
        print(f"{'=' * 50}")

    def formatear_tabla(self, datos, tipo="articulos"):
        """Formatear datos para mostrar en tabla"""
        if tipo == "articulos":
            return [[d[0], d[1], d[2], f"{d[3]:.2f}", f"${d[4]:.2f}", f"${d[3] * d[4]:.2f}"] for d in datos]
        else:  # gastos
            return [[d[0], d[1], f"${d[2]:.2f}", d[3], d[4][:16]] for d in datos]

    def registrar_articulo(self):
        print(f"\n{Fore.GREEN}--- REGISTRAR ARTÍCULO ---")

        nombre = self.input_validado("Nombre: ", lambda x: len(x) > 0, "Nombre requerido")
        categoria = self.input_validado("Categoría: ", lambda x: len(x) > 0, "Categoría requerida")
        cantidad = float(self.input_validado("Cantidad: ", lambda x: x.replace('.', '').isdigit() and float(x) > 0,
                                             "Cantidad debe ser positiva"))
        precio = float(self.input_validado("Precio: $", lambda x: x.replace('.', '').isdigit() and float(x) > 0,
                                           "Precio debe ser positivo"))
        descripcion = input(f"{Fore.WHITE}Descripción (opcional): ")

        if self.db.insertar_articulo(nombre, categoria, cantidad, precio, descripcion):
            print(f"{Fore.GREEN}✅ Artículo registrado exitosamente")
        else:
            print(f"{Fore.RED}❌ Error al registrar")

    def buscar_articulos(self):
        print(f"\n{Fore.GREEN}--- BUSCAR ARTÍCULOS ---")
        opciones = {"1": "nombre", "2": "categoria"}

        opcion = self.input_validado("Buscar por: 1)Nombre 2)Categoría: ", lambda x: x in opciones)
        valor = self.input_validado("Valor a buscar: ")

        resultados = self.db.obtener_articulos(opciones[opcion], valor)
        self._mostrar_articulos(resultados, f"Búsqueda por {opciones[opcion]}")

    def editar_articulo(self):
        print(f"\n{Fore.GREEN}--- EDITAR ARTÍCULO ---")

        id_art = int(self.input_validado("ID del artículo: ", lambda x: x.isdigit() and int(x) > 0))
        articulos = self.db.obtener_articulos()
        articulo = next((a for a in articulos if a[0] == id_art), None)

        if not articulo:
            print(f"{Fore.RED}Artículo no encontrado")
            return

        print(f"\n{Fore.CYAN}Artículo actual:")
        self._mostrar_articulos([articulo])

        print(f"\n{Fore.YELLOW}Deje vacío para mantener valor actual")
        nombre = input(f"Nombre [{articulo[1]}]: ") or articulo[1]
        categoria = input(f"Categoría [{articulo[2]}]: ") or articulo[2]
        cantidad = input(f"Cantidad [{articulo[3]}]: ")
        cantidad = float(cantidad) if cantidad else articulo[3]
        precio = input(f"Precio [{articulo[4]}]: ")
        precio = float(precio) if precio else articulo[4]
        descripcion = input(f"Descripción [{articulo[5] or ''}]: ") or articulo[5] or ""

        if self.db.actualizar_articulo(id_art, nombre, categoria, cantidad, precio, descripcion):
            print(f"{Fore.GREEN}✅ Artículo actualizado")
        else:
            print(f"{Fore.RED}❌ Error al actualizar")

    def eliminar_articulo(self):
        print(f"\n{Fore.GREEN}--- ELIMINAR ARTÍCULO ---")

        id_art = int(self.input_validado("ID del artículo: ", lambda x: x.isdigit() and int(x) > 0))
        articulos = self.db.obtener_articulos()
        articulo = next((a for a in articulos if a[0] == id_art), None)

        if not articulo:
            print(f"{Fore.RED}Artículo no encontrado")
            return

        self._mostrar_articulos([articulo])
        confirmar = self.input_validado(f"{Fore.RED}¿Eliminar? (s/n): ", lambda x: x.lower() in ['s', 'n'])

        if confirmar.lower() == 's':
            if self.db.eliminar_articulo(id_art):
                print(f"{Fore.GREEN}✅ Artículo eliminado")
            else:
                print(f"{Fore.RED}❌ Error al eliminar")

    def listar_articulos(self):
        articulos = self.db.obtener_articulos()
        self._mostrar_articulos(articulos, "TODOS LOS ARTÍCULOS")

    def _mostrar_articulos(self, articulos, titulo="ARTÍCULOS"):
        if not articulos:
            print(f"{Fore.YELLOW}No se encontraron artículos")
            return

        print(f"\n{Fore.GREEN}--- {titulo} ---")
        datos = self.formatear_tabla(articulos, "articulos")
        headers = ["ID", "Nombre", "Categoría", "Cantidad", "Precio", "Total"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))

        total = sum(a[3] * a[4] for a in articulos)
        print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL: ${total:.2f}")

    def exportar_csv(self):
        articulos = self.db.obtener_articulos()
        if not articulos:
            print(f"{Fore.YELLOW}No hay artículos para exportar")
            return

        archivo = self.input_validado("Nombre del archivo: ") + ".csv"

        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Nombre', 'Categoría', 'Cantidad', 'Precio', 'Total', 'Descripción'])

            for a in articulos:
                writer.writerow([a[0], a[1], a[2], a[3], a[4], a[3] * a[4], a[5] or ""])

        print(f"{Fore.GREEN}✅ Exportado a {archivo}")

    def registrar_gasto(self):
        print(f"\n{Fore.GREEN}--- REGISTRAR GASTO ---")

        desc = self.input_validado("Descripción: ", lambda x: len(x) > 0)
        monto = float(self.input_validado("Monto: $", lambda x: x.replace('.', '').isdigit() and float(x) > 0))
        categoria = self.input_validado("Categoría: ", lambda x: len(x) > 0)

        if self.db.insertar_gasto(desc, monto, categoria):
            print(f"{Fore.GREEN}✅ Gasto registrado")
        else:
            print(f"{Fore.RED}❌ Error al registrar gasto")

    def ver_gastos(self):
        opcion = input(f"{Fore.YELLOW}Ver por categoría? (s/n): ").lower()

        if opcion == 's':
            categoria = self.input_validado("Categoría: ")
            gastos = self.db.obtener_gastos(categoria)
            titulo = f"GASTOS - {categoria.upper()}"
        else:
            gastos = self.db.obtener_gastos()
            titulo = "TODOS LOS GASTOS"

        if not gastos:
            print(f"{Fore.YELLOW}No se encontraron gastos")
            return

        print(f"\n{Fore.GREEN}--- {titulo} ---")
        datos = self.formatear_tabla(gastos, "gastos")
        headers = ["ID", "Descripción", "Monto", "Categoría", "Fecha"]
        print(tabulate(datos, headers=headers, tablefmt="fancy_grid"))

        total = sum(g[2] for g in gastos)
        print(f"\n{Fore.GREEN}{Style.BRIGHT}TOTAL GASTOS: ${total:.2f}")

    def visualizar_gastos(self):
        gastos = self.db.obtener_gastos()
        if not gastos:
            print(f"{Fore.YELLOW}No hay gastos para visualizar")
            return

        # Agrupar por categoría
        categorias = {}
        for gasto in gastos:
            cat = gasto[3]
            categorias[cat] = categorias.get(cat, 0) + gasto[2]

        # Crear gráfico
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Gráfico de barras
        cats = list(categorias.keys())
        valores = list(categorias.values())
        ax1.bar(cats, valores, color='skyblue')
        ax1.set_title('Gastos por Categoría')
        ax1.set_ylabel('Monto ($)')
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

        # Gráfico circular
        ax2.pie(valores, labels=cats, autopct='%1.1f%%')
        ax2.set_title('Distribución de Gastos')

        plt.tight_layout()
        plt.show()

    def reporte_completo(self):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}--- REPORTE COMPLETO ---")

        articulos = self.db.obtener_articulos()
        gastos = self.db.obtener_gastos()

        # Estadísticas generales
        total_presupuesto = sum(a[3] * a[4] for a in articulos) if articulos else 0
        total_gastos = sum(g[2] for g in gastos) if gastos else 0
        balance = total_presupuesto - total_gastos

        print(f"\n{Fore.CYAN}📊 RESUMEN GENERAL:")
        print(f"Artículos registrados: {len(articulos)}")
        print(f"Presupuesto total: ${total_presupuesto:.2f}")
        print(f"Gastos totales: ${total_gastos:.2f}")
        print(f"Balance: ${balance:.2f}")

        if balance > 0:
            print(f"{Fore.GREEN}✅ Presupuesto positivo")
        elif balance < 0:
            print(f"{Fore.RED}⚠️ Sobrepresupuesto: ${abs(balance):.2f}")
        else:
            print(f"{Fore.YELLOW}⚖️ Presupuesto equilibrado")

    def ejecutar(self):
        opciones = {
            "1": self.registrar_articulo, "2": self.buscar_articulos, "3": self.editar_articulo,
            "4": self.eliminar_articulo, "5": self.listar_articulos, "6": self.exportar_csv,
            "7": self.registrar_gasto, "8": self.ver_gastos, "9": self.visualizar_gastos,
            "10": self.reporte_completo, "11": self._salir
        }

        print(f"{Fore.CYAN}{Style.BRIGHT}¡Bienvenido al Sistema de Presupuesto!")

        while self.running:
            self.mostrar_menu()
            opcion = self.input_validado(
                "Seleccione opción (1-11): ",
                lambda x: x in opciones.keys(),
                "Opción inválida"
            )

            try:
                opciones[opcion]()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operación cancelada")
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}")

    def _salir(self):
        self.running = False
        self.db.cerrar()
        print(f"{Fore.CYAN}¡Hasta luego!")


if __name__ == "__main__":
    app = GestorPresupuesto()
    try:
        app.ejecutar()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programa interrumpido")
        app.db.cerrar()
    except Exception as e:
        print(f"{Fore.RED}Error inesperado: {e}")
        app.db.cerrar()