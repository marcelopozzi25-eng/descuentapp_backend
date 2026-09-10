import sqlite3
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido al backend de DESCUENTApp!",
        "estado": "funcionando"
    }


@app.get("/ofertas")
def obtener_ofertas():
    conexion = sqlite3.connect("descuentapp.db")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ofertas")

    ofertas = [dict(fila) for fila in cursor.fetchall()]
    conexion.close()

    return ofertas

@app.get("/ofertas/banco/{banco}")
def obtener_ofertas_por_banco(banco: str):
    conexion = sqlite3.connect("descuentapp.db")
    conexion.row_factory = sqlite3.Row

    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM ofertas WHERE banco = ?",
        (banco,)
    )

    ofertas = [dict(fila) for fila in cursor.fetchall()]


    conexion.close()

    return ofertas
