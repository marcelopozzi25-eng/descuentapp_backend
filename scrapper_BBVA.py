import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from datetime import date
URL = "https://www.bbva.com.ar/personas/productos/cuenta-sueldo.html"

def obtener_fuente(conexion):
    cursor = conexion.cursor()

    nombre = "BBVA Argentina"
    tipo = "Banco"
    url = URL
    fecha_verificacion = date.today().isoformat()

    cursor.execute("""
        SELECT id
        FROM fuentes
        WHERE nombre = ? AND url = ?
    """, (nombre, url))

    fila = cursor.fetchone()

    if fila:
        fuente_id = fila[0]

        cursor.execute("""
            UPDATE fuentes
            SET fecha_verificacion = ?
            WHERE id = ?
        """, (fecha_verificacion, fuente_id))

    else:
        cursor.execute("""
            INSERT INTO fuentes
                (nombre, tipo, url, fecha_verificacion)
            VALUES (?, ?, ?, ?)
        """, (nombre, tipo, url, fecha_verificacion))

        fuente_id = cursor.lastrowid

    return fuente_id
conexion = sqlite3.connect("descuentapp.db")

fuente_id = obtener_fuente(conexion)

conexion.commit()

print("Fuente BBVA registrada con ID:", fuente_id)


def obtener_comercio(conexion, nombre, categoria):
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM comercios
        WHERE nombre = ? AND categoria = ?
    """, (nombre, categoria))

    fila = cursor.fetchone()

    if fila:
        return fila[0]

    cursor.execute("""
        INSERT INTO comercios (nombre, categoria)
        VALUES (?, ?)
    """, (nombre, categoria))

    return cursor.lastrowid


def guardar_promocion(conexion, registro, comercio_id, fuente_id):
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM promociones
        WHERE comercio_id = ?
          AND fuente_id = ?
          AND proveedor_beneficio = ?
          AND descuento = ?
          AND dias = ?
          AND vigencia_desde = ?
          AND vigencia_hasta = ?
    """, (
        comercio_id,
        fuente_id,
        registro["proveedor_beneficio"],
        registro["descuento"],
        registro["dias"],
        registro["vigencia_desde"],
        registro["vigencia_hasta"],
    ))

    fila = cursor.fetchone()

    if fila:
        return fila[0]

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
            condiciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        comercio_id,
        fuente_id,
        registro["proveedor_beneficio"],
        registro["tipo_proveedor"],
        registro["tipo_beneficio"],
        registro["descuento"],
        registro["dias"],
        registro["tope"],
        registro["medio_pago"],
        registro["vigencia_desde"],
        registro["vigencia_hasta"],
        registro["condiciones"],
    ))

    return cursor.lastrowid
# --------------------------------------------------------
# DESCARGAR PÁGINA
# --------------------------------------------------------

try:
   respuesta = requests.get(
    URL,
    timeout=30,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/avif,image/webp,"
            "image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }
)
except requests.RequestException as error:
    print("Error al conectar con BBVA:")
    print(error)
    raise SystemExit

print("Código HTTP:", respuesta.status_code)

if respuesta.status_code != 200:
    print("No se pudo obtener correctamente la página de BBVA.")
    raise SystemExit

soup = BeautifulSoup(respuesta.text, "html.parser")

texto_pagina = soup.get_text(" ", strip=True)

frase = "en locales adheridos:"

posicion = texto_pagina.lower().find(frase.lower())
patron_vigencia = re.compile(
    r"Supermercados:\s*promoción válida\s+"
    r"(\d{1,2}/\d{1,2})/{1,2}(\d{4})\s+al\s+"
    r"(\d{1,2}/\d{1,2})/{1,2}(\d{4})",
    re.IGNORECASE
)

vigencia = patron_vigencia.search(texto_pagina)

if vigencia:
    dia_mes_desde, anio_desde, dia_mes_hasta, anio_hasta = vigencia.groups()

    vigencia_desde = f"{dia_mes_desde}/{anio_desde}"
    vigencia_hasta = f"{dia_mes_hasta}/{anio_hasta}"

    print("Vigencia desde:", vigencia_desde)
    print("Vigencia hasta:", vigencia_hasta)
else:
    print("No se encontró la vigencia de supermercados.")
if posicion != -1:
    inicio = max(0, posicion - 1200)
    fin = min(len(texto_pagina), posicion + 2500)

    print(texto_pagina[inicio:fin])
else:
    print("No se encontró la frase.")
import re


print("\n--- EXTRACCIÓN DE PROMOCIONES CONCRETAS ---\n")

patron = re.compile(
    r"(Día|Jumbo|Vea|Disco):\s*"
    r"(\d+)% de reintegro\s*"
    r"([^\.]+)\.\s*"
    r"Para compras mayores a\s*\$([\d\.]+)"
    r"\s*\(tope\s*\$([\d\.]+) por mes\)",
    re.IGNORECASE
)

promociones = patron.findall(texto_pagina)

registros = []

for promocion in promociones:
    comercio, porcentaje, dias, minimo, tope = promocion

    registro = {
        "proveedor_beneficio": "BBVA",
        "tipo_proveedor": "Banco",
        "tipo_beneficio": "Reintegro",
        "comercio": comercio.strip(),
        "categoria": "Supermercados",
        "descuento": porcentaje + "%",
        "dias": dias.strip(),
        "tope": "$" + tope,
        "medio_pago": "QR MODO a través de App BBVA",
        "vigencia_desde": (
    f"{anio_desde}-{dia_mes_desde[3:5]}-{dia_mes_desde[0:2]}"
    if vigencia
    else ""
),
"vigencia_hasta": (
    f"{anio_hasta}-{dia_mes_hasta[3:5]}-{dia_mes_hasta[0:2]}"
    if vigencia
    else ""
),
        "condiciones": (
            "Para compras mayores a $" + minimo +
            ". Tope de $" + tope + " por mes."
        ),
        "fuente": "BBVA Argentina",
        "fuente_url": URL,
    }

    registros.append(registro)

print("\n--- REGISTROS ESTRUCTURADOS ---\n")

for registro in registros:
    print(registro)
    print()

comercios_ids = {}

for registro in registros:
    comercio_id = obtener_comercio(
        conexion,
        registro["comercio"],
        registro["categoria"]
    )

    comercios_ids[registro["comercio"]] = comercio_id

conexion.commit()

print("Comercios registrados:", comercios_ids)

promociones_ids = {}

for registro in registros:
    comercio_id = comercios_ids[registro["comercio"]]

    promocion_id = guardar_promocion(
        conexion,
        registro,
        comercio_id,
        fuente_id
    )

    promociones_ids[registro["comercio"]] = promocion_id

conexion.commit()

print("Promociones registradas:", promociones_ids)

print("\n--- BLOQUES DE BENEFICIOS ENCONTRADOS ---\n")

bloques = soup.select(".submarqueedescription__content")

print("Cantidad de bloques encontrados:", len(bloques))

# --------------------------------------------------------
# PALABRAS PARA DETECTAR COMERCIOS
# --------------------------------------------------------

palabras_comercio = [
    "supermercado",
    "supermercados",
    "changuito",
    "jumbo",
    "vea",
    "disco",
    "día",
    "farmacia",
    "restaurante",
    "gastronomía",
    "combustible",
    "indumentaria",
    "tecnología",
]

# --------------------------------------------------------
# RECORRER BENEFICIOS
# --------------------------------------------------------

for i, bloque in enumerate(bloques, start=1):

    titulo = bloque.select_one(
        ".submarqueedescription__title"
    )

    descripcion = bloque.select_one(
        ".submarqueedescription__text"
    )

    enlace = bloque.select_one("a")

    titulo_texto = (
        titulo.get_text(" ", strip=True)
        if titulo
        else ""
    )

    descripcion_texto = (
        descripcion.get_text(" ", strip=True)
        if descripcion
        else ""
    )

    texto_completo = (
        titulo_texto + " " + descripcion_texto
    ).lower()

    # ----------------------------------------------------
    # FILTRO
    # ----------------------------------------------------

    es_comercio = any(
        palabra in texto_completo
        for palabra in palabras_comercio
    )

    if not es_comercio:
        continue

    # ----------------------------------------------------
    # EXTRACCIÓN DE DATOS
    # ----------------------------------------------------

    proveedor = "BBVA"

    categoria = "Supermercados"

    descuento = ""
    if "20%" in descripcion_texto:
        descuento = "Hasta 20%"

    dias = ""
    if "todas las semanas" in descripcion_texto.lower():
        dias = "Todas las semanas"

    medio_pago = ""
    if "modo" in descripcion_texto.lower():
        medio_pago = "Tarjetas de crédito a través de MODO"

    # ----------------------------------------------------
    # DATOS ESTRUCTURADOS
    # ----------------------------------------------------

    promocion = {
        "proveedor_beneficio": proveedor,
        "tipo_proveedor": "Banco",
        "tipo_beneficio": "Reintegro / descuento",
        "categoria": categoria,
        "descuento": descuento,
        "dias": dias,
        "tope": "",
        "medio_pago": medio_pago,
        "vigencia_desde": "",
        "vigencia_hasta": "",
        "condiciones": descripcion_texto,
        "fuente": "BBVA Argentina",
        "fuente_url": (
            enlace.get("href")
            if enlace
            else URL
        ),
    }

    # ----------------------------------------------------
    # MOSTRAR RESULTADO
    # ----------------------------------------------------

    print(f"\n### PROMOCIÓN {i} ###")

    print("Proveedor:", proveedor)
    print("Categoría:", categoria)
    print("Descuento:", descuento)
    print("Días:", dias)
    print("Medio de pago:", medio_pago)
    print("Título:", titulo_texto)
    print("Descripción:", descripcion_texto)

    if enlace:
        print("URL:", enlace.get("href"))

    print("\n--- DATOS ESTRUCTURADOS ---")
    print(promocion)