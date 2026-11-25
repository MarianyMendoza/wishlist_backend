from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import articulos, auth, categorias, estados, imagenes, scraper, usuarios

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wish List API")

origenes_permitidos = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(estados.router)
app.include_router(articulos.router)
app.include_router(scraper.router)
app.include_router(imagenes.router)