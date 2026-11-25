from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class CategoriaBase(BaseModel):
    nombre_categoria: str

class CategoriaCrear(CategoriaBase):
    pass

class CategoriaRespuesta(CategoriaBase):
    id_categoria: int

    class Config:
        from_attributes = True

class EstadoRespuesta(BaseModel):
    id_estado: int
    nombre_estado: str

    class Config:
        from_attributes = True

class  UsuarioBase(BaseModel):
    nombre_usuario: str
    email: str
    
class UsuarioCrear(UsuarioBase):
   
   contrasena: str

class UsuarioRespuesta(UsuarioBase):
    id_usuario: int
    uid_usuario: UUID

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: str
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str

class  ArticulosBase(BaseModel):
    marca : str
    nombre_articulo: str
    precio: float
    prioridad :int | None = None
    imagen: str | None = None
    url: str | None = None
    talla : str | None = None
    color: str | None = None
    

    
class ArticulosCrear(ArticulosBase):
    nombre_categoria: str
    pass

class ArticulosRespuesta(ArticulosBase):
    id_articulo: int
    id_categoria: int
    id_estado: int
    id_usuario: int
    fecha_agregado: datetime
    fecha_comprado: datetime | None = None
    id_usuario_cambio_estado: int | None = None


    class Config:
        from_attributes = True

class ScraperEntrada(BaseModel):
    url: str


class ScraperRespuesta(BaseModel):
    url: str
    nombre_articulo: str | None = None
    marca: str | None = None
    imagen: str | None = None
    precio: float | None = None




