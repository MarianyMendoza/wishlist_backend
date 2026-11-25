import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, UUID, ForeignKey,Text,DateTime, Float
from database import Base



class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria= Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String, index=True)

class Usuarios(Base):
    __tablename__ = "usuarios"

    id_usuario= Column(Integer, primary_key=True, index=True)
    uid_usuario = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True)
    nombre_usuario = Column(String, index=True)
    email = Column(String, index=True)
    contrasena_hash = Column(String, nullable=False)

class Articulos (Base):
    __tablename__ = "articulos"

    id_articulo = Column(Integer, primary_key=True, index=True)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"))
    marca = Column(String, index=True)
    nombre_articulo = Column(String, index=True)
    precio = Column(Float, index=True)
    prioridad = Column(Integer,index=True)
    imagen = Column(Text)
    url = Column(Text)
    talla = Column(String, index=True, nullable=True)
    color = Column(String, index=True, nullable=True)
    id_estado = Column(Integer, ForeignKey("estado.id_estado"))
    fecha_agregado = Column(DateTime, default=func.now())
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha_comprado = Column(DateTime, nullable=True)
    id_usuario_cambio_estado = Column(Integer, nullable=True)

class Estado (Base):
    __tablename__ = "estado"

    id_estado = Column(Integer, primary_key=True, index=True)
    nombre_estado = Column(String, index=True)

