import sqlite3

conexion = sqlite3.connect("descuentapp.db")
cursor = conexion.cursor()

# ------------------------------------------------------------
# 1. Fuente oficial
# ------------------------------------------------------------

cursor.execute("""
INSERT INTO fuentes (
    nombre,
    tipo,
    url,
    fecha_verificacion
)
VALUES (?, ?, ?, ?)
""", (
    "BBVA Argentina",
    "oficial",
    "https://www.bbva.com.ar/personas/productos/cuenta-sueldo.html",
    "2026-09-11"
))

fuente_id = cursor.lastrowid


# ------------------------------------------------------------
# 2. Comercio
# ------------------------------------------------------------

cursor.execute("""
INSERT INTO comercios (
    nombre,
    categoria
)
VALUES (?, ?)
""", (
    "Día",
    "Supermercados"
))

comercio_id = cursor.lastrowid


# ------------------------------------------------------------
# 3. Promoción
# ------------------------------------------------------------

cursor.execute("""
INSERT INTO promociones (
    comercio_id,
    fuente_id,
    proveedor_beneficio,
    tipo_proveedor,
    tipo_beneficio,
    descuento,
    dias,
    tope,
    medio_pago,
    vigencia_desde,
    vigencia_hasta,
    condiciones,
    activa
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    comercio_id,
    fuente_id,
    "BBVA",
    "Banco",
    "Reintegro",
    "20%",
    "Viernes y sábados",
    "$20.000 por mes",
    "QR MODO desde la App BBVA",
    "2026-09-01",
    "2026-09-30",
    "Compra mínima de $35.000. Válido en locales adheridos. Requiere caja de ahorro en pesos activa en BBVA vinculada a MODO. No aplica a otras billeteras virtuales.",
    1
))

conexion.commit()
conexion.close()

print("Promoción real cargada correctamente.")