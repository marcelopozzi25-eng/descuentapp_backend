import sqlite3
from fastapi import FastAPI

app = FastAPI()


def obtener_conexion():
    conexion = sqlite3.connect("descuentapp.db")
    conexion.row_factory = sqlite3.Row
    return conexion


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido al backend de DESCUENTApp!",
        "estado": "funcionando"
    }


@app.get("/ofertas")
def obtener_ofertas():
    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            p.id,
            c.nombre AS supermercado,
            p.descuento AS titulo,
            p.proveedor_beneficio AS banco,
            c.categoria,
            p.dias,
            p.tope,
            p.medio_pago,
            p.vigencia_desde,
            p.vigencia_hasta,
            p.condiciones,
            f.nombre AS fuente,
            f.url AS fuente_url
        FROM promociones p
        INNER JOIN comercios c
            ON p.comercio_id = c.id
        INNER JOIN fuentes f
            ON p.fuente_id = f.id
        WHERE p.activa = 1
    """)

    ofertas = [dict(fila) for fila in cursor.fetchall()]

    conexion.close()

    return ofertas


@app.get("/ofertas/banco/{banco}")
def obtener_ofertas_por_banco(banco: str):
    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            p.id,
            c.nombre AS supermercado,
            p.descuento AS titulo,
            p.proveedor_beneficio AS banco,
            c.categoria,
            p.dias,
            p.tope,
            p.medio_pago,
            p.vigencia_desde,
            p.vigencia_hasta,
            p.condiciones,
            f.nombre AS fuente,
            f.url AS fuente_url
        FROM promociones p
        INNER JOIN comercios c
            ON p.comercio_id = c.id
        INNER JOIN fuentes f
            ON p.fuente_id = f.id
        WHERE p.activa = 1
          AND p.proveedor_beneficio = ?
    """, (banco,))

    ofertas = [dict(fila) for fila in cursor.fetchall()]

    conexion.close()

    return ofertas