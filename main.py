from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base 
from models import Vuelo
from flight_list import ListaDoblementeEnlazada

Base.metadata.create_all(bind=engine)
app = FastAPI()
lista = ListaDoblementeEnlazada()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/vuelos/")
def crear_vuelo(codigo: str, destino: str, prioridad: str, db: Session = Depends(get_db)):
    vuelo = Vuelo(codigo=codigo, destino=destino, prioridad=prioridad)
    db.add(vuelo)
    db.commit()
    db.refresh(vuelo)

    if prioridad == "emergencia":
        lista.insertar_al_frente(vuelo)
    elif prioridad == "demorado":
        lista.insertar_en_posicion(vuelo, 1)
    else:
        lista.insertar_al_final(vuelo)
    return vuelo

@app.get("/vuelos/primero")
def ver_primero():
    vuelo = lista.obtener_primero()
    if vuelo:
        return vuelo
    raise HTTPException(status_code=404, detail="No hay vuelos")

@app.get("/vuelos/ultimo")
def ver_ultimo():
    vuelo = lista.obtener_ultimo()
    if vuelo:
        return vuelo
    raise HTTPException(status_code=404, detail="No hay vuelos")

@app.get("/vuelos/longitud")
def obtener_longitud():
    return {"total": lista.longitud()}

@app.delete("/vuelos/{posicion}")
def eliminar_vuelo(posicion: int):
    vuelo = lista.extraer_de_posicion(posicion)
    if vuelo:
        return vuelo
    raise HTTPException(status_code=404, detail="Posición inválida")

#python -m uvicorn main:app --reload
