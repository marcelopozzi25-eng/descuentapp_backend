import sqlite3
import json
from datetime import datetime

DB = "descuentapp.db"
JSON_FILE = "supervielle_beneficios.json"

# ============================================================
# CARGAR JSON
# ============================================================

with open(JSON_FILE, "r", encoding="utf-8") as archivo:
    promociones = json.load(archivo)

print(f"Promociones Supervielle encontradas en JSON: {len(promociones)}")

# ============================================================
# CONECTAR BASE
# ============================================================

conexion = sqlite3.connect(DB)
cursor = conexion.cursor()

# ============================================================
# 1. CREAR / BUSCAR FUENTE SUPERVIELLE
# ============================================================

nombre_fuente = "Supervielle"
url_fuente = "https://www.supervielle.com.ar/personas/beneficios/descuentos"

cursor.execute(
    """
    SELECT id
    FROM fuentes
    WHERE nombre = ?
    """,
    (nombre_fuente,)
)

fila = cursor.fetchone()

if fila:
    fuente_id = fila[0]
    print(f"Fuente Supervielle ya existe. ID: {fuente_id}")

else:
    cursor.execute(
        """
        INSERT INTO fuentes (
            nombre,
            tipo,
            url,
            fecha_verificacion
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            nombre_fuente,
            "Banco",
            url_fuente,
            datetime.now().isoformat(timespec="seconds")
        )
    )

    fuente_id = cursor.lastrowid
    print(f"Fuente Supervielle creada. ID: {fuente_id}")

# ============================================================
# 2. IMPORTAR COMERCIOS Y PROMOCIONES
# ============================================================

insertadas = 0
omitidas = 0

for promo in promociones:

    nombre_comercio = promo.get("comercio")

    if not nombre_comercio:
        print("Promoción sin comercio. Se omite.")
        omitidas += 1
        continue

    categoria = promo.get("rubro") or "Otros"

    # --------------------------------------------------------
    # BUSCAR COMERCIO
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM comercios
        WHERE LOWER(nombre) = LOWER(?)
        """,
        (nombre_comercio,)
    )

    fila_comercio = cursor.fetchone()

    if fila_comercio:
        comercio_id = fila_comercio[0]

    else:
        cursor.execute(
            """
            INSERT INTO comercios (
                nombre,
                categoria,
                activo
            )
            VALUES (?, ?, 1)
            """,
            (
                nombre_comercio,
                categoria
            )
        )

        comercio_id = cursor.lastrowid

        print(
            f"Nuevo comercio creado: "
            f"{nombre_comercio} "
            f"(categoría: {categoria}, ID {comercio_id})"
        )

    # --------------------------------------------------------
    # EVITAR DUPLICADOS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM promociones
        WHERE comercio_id = ?
          AND fuente_id = ?
          AND proveedor_beneficio = ?
          AND descuento = ?
          AND dias = ?
          AND vigencia_desde = ?
          AND vigencia_hasta = ?
        """,
        (
            comercio_id,
            fuente_id,
            promo.get("proveedor_beneficio"),
            str(promo.get("descuento")),
            promo.get("dias"),
            promo.get("vigencia_desde"),
            promo.get("vigencia_hasta"),
        )
    )

    if cursor.fetchone():

        print(
            f"Ya existe: "
            f"{nombre_comercio} | "
            f"{promo.get('descuento')} | "
            f"{promo.get('dias')}"
        )

        omitidas += 1
        continue

    # --------------------------------------------------------
    # INSERTAR PROMOCIÓN
    # --------------------------------------------------------

    cursor.execute(
        """
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            comercio_id,
            fuente_id,
            promo.get("proveedor_beneficio"),
            promo.get("tipo_proveedor"),
            promo.get("tipo_beneficio"),
            str(promo.get("descuento")),
            promo.get("dias"),
            str(promo.get("tope")),
            promo.get("medio_pago"),
            promo.get("vigencia_desde"),
            promo.get("vigencia_hasta"),
            promo.get("condiciones"),
        )
    )

    insertadas += 1

    print(
        f"INSERTADA: "
        f"{nombre_comercio} | "
        f"{promo.get('descuento')} | "
        f"{promo.get('dias')}"
    )

# ============================================================
# GUARDAR
# ============================================================

conexion.commit()

# ============================================================
# RESUMEN
# ============================================================

print()
print("=" * 60)
print("IMPORTACIÓN SUPERVIELLE FINALIZADA")
print("=" * 60)

print(f"Promociones en JSON : {len(promociones)}")
print(f"Promociones nuevas  : {insertadas}")
print(f"Promociones omitidas: {omitidas}")

# ============================================================
# VERIFICACIÓN
# ============================================================

cursor.execute(
    """
    SELECT proveedor_beneficio, COUNT(*)
    FROM promociones
    GROUP BY proveedor_beneficio
    ORDER BY proveedor_beneficio
    """
)

print()
print("PROMOCIONES POR PROVEEDOR:")

for proveedor, cantidad in cursor.fetchall():
    print(f"  {proveedor}: {cantidad}")

conexion.close()

print()
print("Base de datos cerrada correctamente.")