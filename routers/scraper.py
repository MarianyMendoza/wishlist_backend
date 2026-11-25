import json
import re

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from fastapi import APIRouter, Depends, HTTPException

import models
import schemas
from routers.auth import obtener_usuario_actual

router = APIRouter(tags=["Scraper"])


def obtener_meta(soup: BeautifulSoup, propiedades: list[str]) -> str | None:
   
    for prop in propiedades:
        etiqueta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if etiqueta and etiqueta.get("content"):
            return etiqueta["content"].strip()
    return None


def limpiar_precio(valor: str | None) -> float | None:
    if not valor:
        return None
    limpio = re.sub(r"[^\d.,]", "", valor)
    if not limpio:
        return None

    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        if re.fullmatch(r"\d{1,3}(,\d{3})+", limpio):
            limpio = limpio.replace(",", "")
        else:
            limpio = limpio.replace(",", ".")
    elif "." in limpio:
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", limpio):
            limpio = limpio.replace(".", "")
            

    try:
        return float(limpio)
    except ValueError:
        return None

def buscar_producto_en_json(data) -> dict | None:
    if isinstance(data, dict):
        tipo = data.get("@type")

        if tipo in ("Product", "ProductGroup") or (
            isinstance(tipo, list) and ("Product" in tipo or "ProductGroup" in tipo)
        ):
            return data
        
        if "@graph" in data:
            return buscar_producto_en_json(data["@graph"])
        
    elif isinstance(data, list):
            for item in data:
                resultado = buscar_producto_en_json(item)
                if resultado:
                    return resultado
    return None


def obtener_precio_json_ld(soup: BeautifulSoup) -> float | None:
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        contenido = script.get_text(strip=True)
        if not contenido:
            continue
        try:
            datos = json.loads(contenido)
        except json.JSONDecodeError:
            continue

        producto = buscar_producto_en_json(datos)
        if not producto:
            continue

        ofertas = producto.get("offers")
  
        if not ofertas and isinstance(producto.get("hasVariant"), list):
            for variante in producto["hasVariant"]:
                if isinstance(variante, dict) and variante.get("offers"):
                    ofertas = variante["offers"]
                    break

        if isinstance(ofertas, list) and ofertas:
            ofertas = ofertas[0]

        if isinstance(ofertas, dict):
            precio_crudo = ofertas.get("price") or ofertas.get("lowPrice")
            if precio_crudo is not None:
                return limpiar_precio(str(precio_crudo))

    return None

def obtener_precio_microdata(soup: BeautifulSoup) -> float | None:

    etiqueta = soup.find(attrs={"itemprop": "price"})
    if not etiqueta:
        return None
    valor = etiqueta.get("content") or etiqueta.get_text(strip=True)
    return limpiar_precio(valor)


@router.post("/scraper/extraer", response_model=schemas.ScraperRespuesta)
def extraer_datos_url(
    datos: schemas.ScraperEntrada,
    _usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    headers = {
        "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
    }

    try:
        respuesta = curl_requests.get(
            datos.url,
            impersonate="chrome",
            headers=headers,
            allow_redirects=True,
            timeout=15
        )
    except Exception:
        raise HTTPException(
        status_code=400,
        detail="No se pudo conectar con la URL proporcionada"
        )

    if respuesta.status_code >= 400:
        raise HTTPException(
        status_code=400,
        detail=f"La tienda rechazó la consulta (código {respuesta.status_code})"
        )

    soup = BeautifulSoup(respuesta.text, "html.parser")
    

    nombre = obtener_meta(soup, ["og:title", "twitter:title"])
    if not nombre and soup.title and soup.title.string:
        nombre = soup.title.string.strip()

    imagen = obtener_meta(soup, ["og:image", "twitter:image"])
    marca = obtener_meta(soup, ["product:brand", "og:site_name"])

    precio_texto = obtener_meta(soup, [
        "product:price:amount",
        "og:price:amount",
        "twitter:data1"
        ])
    precio = limpiar_precio(precio_texto)

    if precio is None:
        precio = obtener_precio_json_ld(soup)
    if precio is None:
        precio = obtener_precio_microdata(soup)

    return schemas.ScraperRespuesta(
        url=datos.url,
        nombre_articulo=nombre,
        marca=marca,
        imagen=imagen,
        precio=precio
        )