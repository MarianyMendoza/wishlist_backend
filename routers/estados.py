from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models


router = APIRouter(tags=["Estados"])


@router.post("/estados/inicializar")

def inicializar_estados(db: Session = Depends(get_db)):
    
    estados_iniciales = ["Pendiente", "Comprado", "Reservado"]

    for nombre in estados_iniciales:
        existe = db.query(models.Estado).filter(models.Estado.nombre_estado == nombre).first()

        if not existe:
            nuevo_estado = models.Estado(nombre_estado=nombre)
            db.add(nuevo_estado)
            db.commit()

    return {"mensaje": "Estados predeterminados cargados exitosamente"}