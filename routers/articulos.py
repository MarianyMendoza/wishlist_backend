from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.auth import obtener_usuario_actual
import models
import schemas
from database import get_db

router = APIRouter(tags=["Artículos"])


@router.post("/articulos", response_model=schemas.ArticulosRespuesta)

def crear_articulo(articulo: schemas.ArticulosCrear, db: Session = Depends(get_db), usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)):

    estado_pendiente = db.query(models.Estado).filter(models.Estado.nombre_estado == "Disponible").first()
    
    if not estado_pendiente:
        raise HTTPException(status_code=500, detail="El estado 'Disponible' no está configurado en la base de datos")
   
    categoria_db = db.query(models.Categoria).filter(models.Categoria.nombre_categoria == articulo.nombre_categoria).first()

    if not categoria_db:
        categoria_db = models.Categoria(nombre_categoria=articulo.nombre_categoria)
        db.add(categoria_db)
        db.commit()
        db.refresh(categoria_db) 

       
    nuevo_articulo = models.Articulos(
        marca=articulo.marca,
        nombre_articulo=articulo.nombre_articulo,
        precio=articulo.precio,
        prioridad=articulo.prioridad,
        imagen=articulo.imagen,
        url=articulo.url,
        talla=articulo.talla,
        color=articulo.color,
        id_categoria=categoria_db.id_categoria,
        id_usuario=usuario_actual.id_usuario,
        id_estado=estado_pendiente.id_estado
        )

    db.add(nuevo_articulo)
    db.commit()
    db.refresh(nuevo_articulo)

    return nuevo_articulo

@router.get("/articulos", response_model=list[schemas.ArticulosRespuesta])

def obtener_articulos(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
    ):

    articulos = db.query(models.Articulos).filter(models.Articulos.id_usuario == usuario_actual.id_usuario).all()
    
    return articulos

@router.put("/articulos/{id_articulo}", response_model=schemas.ArticulosRespuesta)
def actualizar_articulo(
    id_articulo: int,
    articulo_actualizado: schemas.ArticulosCrear,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    articulo_db = db.query(models.Articulos).filter(
        models.Articulos.id_articulo == id_articulo,
        models.Articulos.id_usuario == usuario_actual.id_usuario
    ).first()

    if articulo_db is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado o no autorizado")

    for clave, valor in articulo_actualizado.dict().items():
        setattr(articulo_db, clave, valor)

    db.commit()
    db.refresh(articulo_db)

    return articulo_db

@router.delete("/articulos/{id_articulo}")
def eliminar_articulo(
    id_articulo: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    articulo_db = db.query(models.Articulos).filter(
        models.Articulos.id_articulo == id_articulo,
        models.Articulos.id_usuario == usuario_actual.id_usuario
    ).first()

    if articulo_db is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado o no autorizado")

    db.delete(articulo_db)
    db.commit()

    return {"mensaje": "Artículo eliminado de tu Wish List exitosamente"}

@router.patch("/articulos/{id_articulo}/reservar", response_model=schemas.ArticulosRespuesta)
def reservar_articulo(
    id_articulo: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    
    articulo_db = db.query(models.Articulos).filter(

        models.Articulos.id_articulo == id_articulo

    ).first()

    if articulo_db is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    
    estado_reservado = db.query(models.Estado).filter(
        models.Estado.nombre_estado == "Reservado"
    ).first()

    if not estado_reservado:
        raise HTTPException(
            status_code=500,
            detail="El estado 'Reservado' no está configurado en la base de datos"
        )

    if articulo_db.id_estado == estado_reservado.id_estado:
        raise HTTPException(
            status_code=400,
            detail="Este artículo ya se encuentra reservado"
        )

    
    articulo_db.id_estado = estado_reservado.id_estado
    articulo_db.id_usuario_cambio_estado = usuario_actual.id_usuario

    db.commit()
    db.refresh(articulo_db)

    return articulo_db


@router.get("/articulos/usuario/{id_usuario}", response_model=list[schemas.ArticulosRespuesta])
def obtener_articulos_de_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuarios = Depends(obtener_usuario_actual)
):
    usuario_objetivo = db.query(models.Usuarios).filter(
        models.Usuarios.id_usuario == id_usuario
    ).first()

    if usuario_objetivo is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    articulos = db.query(models.Articulos).filter(
        models.Articulos.id_usuario == id_usuario
    ).all()

    return articulos

@router.get("/articulos/{id_articulo}", response_model=schemas.ArticulosRespuesta)
def obtener_articulo_individual(id_articulo: int, db: Session = Depends(get_db)):

    articulo_db = db.query(models.Articulos).filter(models.Articulos.id_articulo == id_articulo).first()

    if articulo_db is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    return articulo_db