import os

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

import models
from routers.auth import obtener_usuario_actual

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

router = APIRouter(tags=["Imágenes"])

TIPOS_PERMITIDOS = ("image/jpeg", "image/png", "image/webp")


@router.post("/imagenes/subir")
def subir_imagen(
    archivo: UploadFile = File(...),
    _usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Formato no válido. Solo se permiten imágenes JPG, PNG o WEBP."
        )

    try:
        resultado = cloudinary.uploader.upload(
            archivo.file,
            folder="wishlist_app"
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al subir la imagen a Cloudinary."
        )

    return {"url": resultado["secure_url"]}