from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from routers.auth import obtener_hash_password

router = APIRouter(tags=["Usuarios"])

@router.post("/usuarios", response_model=schemas.UsuarioRespuesta)

def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):

    usuario_existente = db.query(models.Usuarios).filter(models.Usuarios.email == usuario.email).first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")

    # Usamos la herramienta importada para encriptar
    contrasena_encriptada = obtener_hash_password(usuario.contrasena)

    nuevo_usuario = models.Usuarios(
        nombre_usuario=usuario.nombre_usuario,
        email=usuario.email,
        contrasena=contrasena_encriptada
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario