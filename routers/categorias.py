from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models


router = APIRouter(tags=["Categorías"])


@router.post("/categorias/inicializar")
def inicializar_categorias(db: Session = Depends(get_db)):
    categorias_iniciales = [
        "Ropa", "Calzado", "Bolsos y carteras",
        "Maquillaje", "Cuidado de la piel", "Papelería",
        "Tecnología", "Videojuegos", "Hogar", "Salud", "Fitness"
    ]
    for nombre in categorias_iniciales:
        existe = db.query(models.Categoria).filter(models.Categoria.nombre_categoria == nombre).first()
        if not existe:
            nueva_categoria = models.Categoria(nombre_categoria=nombre)
            db.add(nueva_categoria)
            db.commit()

    return {"mensaje": "Categorías predeterminadas cargadas exitosamente"}