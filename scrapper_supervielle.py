import json
import sqlite3
import time
import websocket
import requests

# ============================================================
# CONFIGURACIÓN
# ============================================================

CDP_URL = "http://127.0.0.1:9222"
SUPER_VIELLE_URL = (
    "https://www.supervielle.com.ar/api/beneficios"
)

DB_PATH = "descuentapp.db"

RUBROS = [
    "Automotor",
    "Belleza",
    "Carnicerias Mendoza",
    "Carnicerias San Luis",
    "Combustible",
    "Compras",
    "Entretenimiento",
    "Farmacia",
    "Hogar",
    "Indumentaria",
    "Invierno en Chile",
    "Mascotas",
    "Mercado Libre",
    "Opticas",
    "Primer pago NFC MODO",
    "Promos Mastercard",
    "Restaurantes",
    "Supermercados",
    "Tecnologia",
    "Transporte",
    "Turismo",
]


# ============================================================
# BUSCAR PESTAÑA DE SUPERVIELLE
# ============================================================

print("=" * 60)
print("SCRAPER SUPERVIELLE")
print("=" * 60)

print("Buscando pestaña de Supervielle...")

paginas = requests.get(
    f"{CDP_URL}/json/list",
    timeout=10
).json()

pagina = None

for p in paginas:
    if (
        p.get("type") == "page"
        and "supervielle.com.ar/personas/beneficios" in p.get("url", "")
    ):
        pagina = p
        break

if not pagina:
    raise RuntimeError(
        "No encontré una pestaña de Supervielle abierta en Chrome."
    )

print("Pestaña encontrada:")
print(pagina["title"])
print(pagina["url"])


# ============================================================
# CONEXIÓN WEBSOCKET CDP
# ============================================================

print()
print("Conectando directamente al WebSocket de Chrome...")

ws = websocket.create_connection(
    pagina["webSocketDebuggerUrl"],
    origin="http://127.0.0.1:9222",
    timeout=30,
)

print("¡Conectado!")


# ============================================================
# FUNCIÓN PARA EJECUTAR JAVASCRIPT
# ============================================================

contador = 0


def ejecutar_js(script):
    global contador

    contador += 1

    ws.send(json.dumps({
        "id": contador,
        "method": "Runtime.evaluate",
        "params": {
            "expression": script,
            "awaitPromise": True,
            "returnByValue": True,
        },
    }))

    while True:
        respuesta = json.loads(ws.recv())

        if respuesta.get("id") == contador:
            return respuesta


# ============================================================
# CONSULTAR UN RUBRO
# ============================================================

def obtener_beneficios(rubro):

    print(f"  Consultando: {rubro}")

    rubro_js = json.dumps(rubro)

    script = f"""
    fetch(
        '/api/beneficios?rubro=' +
        encodeURIComponent({rubro_js}) +
        '&esIdentite=false'
    )
    .then(r => r.json())
    """

    respuesta = ejecutar_js(script)

    try:
        resultado = respuesta["result"]["result"]["value"]
    except Exception:
        print("  ERROR: respuesta inesperada")
        print(json.dumps(respuesta, indent=2, ensure_ascii=False))
        return []

    if resultado.get("codigo") != "OK":
        print("  ERROR:", resultado)
        return []

    beneficios = resultado.get("beneficios", [])

    print(f"  OK → {len(beneficios)} beneficios")

    return beneficios


# ============================================================
# TRANSFORMAR BENEFICIO
# ============================================================

def transformar(beneficio):

    dias = beneficio.get("dias") or []

    dias_texto = ", ".join(
        str(d).strip()
        for d in dias
        if str(d).strip()
    )

    credito = beneficio.get("esTarjetaCredito", False)
    debito = beneficio.get("esTarjetaDebito", False)

    if credito and debito:
        medio_pago = "Crédito y Débito"
    elif credito:
        medio_pago = "Crédito"
    elif debito:
        medio_pago = "Débito"
    else:
        medio_pago = ""

    condiciones = beneficio.get("descripcionTarjetas") or ""

    cuotas = beneficio.get("cuotas")

    if cuotas:
        condiciones = (
            f"{condiciones} "
            f"Cuotas: {', '.join(map(str, cuotas))}."
        ).strip()

    return {
        "proveedor_beneficio": "Supervielle",
        "tipo_proveedor": "Banco",
        "tipo_beneficio": "Descuento",

        "comercio": beneficio.get("marca"),
        "descuento": beneficio.get("descuento"),
        "dias": dias_texto,
        "tope": beneficio.get("tope"),

        "medio_pago": medio_pago,

        "vigencia_desde": beneficio.get(
            "fechaVigenciaDesde"
        ),

        "vigencia_hasta": beneficio.get(
            "fechaVigenciaHasta"
        ),

        "condiciones": condiciones,

        "logo": beneficio.get("logo"),

        "zonas": beneficio.get("zonas"),

        "id_supervielle": beneficio.get("id"),

        "rubro": beneficio.get("rubro"),
    }


# ============================================================
# OBTENER TODAS LAS PROMOCIONES
# ============================================================

print()
print("Consultando promociones...")
print()

todos = []

for rubro in RUBROS:

    beneficios = obtener_beneficios(rubro)

    for beneficio in beneficios:
        todos.append(
            transformar(beneficio)
        )

    time.sleep(0.2)


print()
print("=" * 60)
print(f"TOTAL OBTENIDO: {len(todos)}")
print("=" * 60)


# ============================================================
# CERRAR WEBSOCKET
# ============================================================

ws.close()


# ============================================================
# GUARDAR RESPALDO JSON
# ============================================================

with open(
    "supervielle_beneficios.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        todos,
        f,
        ensure_ascii=False,
        indent=2,
    )

print()
print("Respaldo guardado:")
print("supervielle_beneficios.json")


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

comercios = sorted(
    set(
        x["comercio"]
        for x in todos
        if x["comercio"]
    )
)

print()
print(f"Comercios distintos: {len(comercios)}")

for comercio in comercios:
    cantidad = sum(
        1
        for x in todos
        if x["comercio"] == comercio
    )

    print(f"  {comercio}: {cantidad}")


print()
print("SCRAPER FINALIZADO CORRECTAMENTE.")