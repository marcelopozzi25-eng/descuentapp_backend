import sqlite3

conexion = sqlite3.connect("descuentapp.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ofertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supermercado TEXT NOT NULL,
    titulo TEXT NOT NULL,
    banco TEXT,
    categoria TEXT
)
""")

cursor.execute("DELETE FROM ofertas")

ofertas = [
    ("COTO", "20% de descuento", "BBVA", "Supermercados"),
    ("Carrefour", "25% de descuento", "Banco Nación", "Supermercados"),
    ("DIA", "30% de descuento", "BBVA", "Supermercados")
]

cursor.executemany("""
INSERT INTO ofertas (supermercado, titulo, banco, categoria)
VALUES (?, ?, ?, ?)
""", ofertas)

conexion.commit()
conexion.close()

print("Base de datos y ofertas cargadas correctamente.")
