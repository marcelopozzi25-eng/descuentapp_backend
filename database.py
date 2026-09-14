import sqlite3

conexion = sqlite3.connect("descuentapp.db")
cursor = conexion.cursor()

# ============================================================
# TABLA: fuentes
# Guarda el origen oficial de la información.
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS fuentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT,
    url TEXT NOT NULL,
    fecha_verificacion TEXT
)
""")


# ============================================================
# TABLA: comercios
# Información básica de cada comercio.
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS comercios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    direccion TEXT,
    localidad TEXT,
    provincia TEXT,
    latitud REAL,
    longitud REAL,
    activo INTEGER NOT NULL DEFAULT 1
)
""")


# ============================================================
# TABLA: promociones
# Beneficios concretos asociados a comercios y fuentes.
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS promociones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    comercio_id INTEGER NOT NULL,
    fuente_id INTEGER NOT NULL,

    proveedor_beneficio TEXT NOT NULL,
    tipo_proveedor TEXT,
    tipo_beneficio TEXT,

    descuento TEXT,
    dias TEXT,
    tope TEXT,
    medio_pago TEXT,

    vigencia_desde TEXT,
    vigencia_hasta TEXT,

    condiciones TEXT,

    activa INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (comercio_id) REFERENCES comercios(id),
    FOREIGN KEY (fuente_id) REFERENCES fuentes(id)
)
""")


conexion.commit()
conexion.close()

print("Base de datos de DESCUENTApp preparada correctamente.")