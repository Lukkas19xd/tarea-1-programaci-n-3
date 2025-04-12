from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, shemas
from cola import Cola

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
cola_misiones = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/personajes")
def registrar_personaje(personaje: shemas.PersonajeCreate, db: Session = Depends(get_db)):
    nuevo = models.Personaje(nombre=personaje.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    cola_misiones[nuevo.id] = Cola()
    return nuevo

@app.post("/misiones")
def crear_mision(mision: shemas.MisionCreate, db: Session = Depends(get_db)):
    nueva = models.Mision(**mision.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).get(personaje_id)
    mision = db.query(models.Mision).get(mision_id)
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o Misión no encontrada")
    
    personaje.misiones.append(mision)
    db.commit()

    if personaje_id not in cola_misiones:
        cola_misiones[personaje_id] = Cola()
    
    cola_misiones[personaje_id].enqueue(mision.id)
    return {"mensaje": "Misión encolada"}

@app.post("/personajes/{personaje_id}/completar")
def completar_mision(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).get(personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    cola = cola_misiones.get(personaje_id)
    if cola is None:
        raise HTTPException(status_code=400, detail="Este personaje no tiene misiones activas")

    mision_id = cola.dequeue()
    if mision_id is None:
        return {"mensaje": "No hay misiones para completar"}

    mision = db.query(models.Mision).get(mision_id)
    if not mision:
        return {"mensaje": "La misión ya no existe"}

    personaje.experiencia += mision.xp
    personaje.misiones.remove(mision)
    db.commit()
    return {"mensaje": "Misión completada", "xp_ganada": mision.xp}

@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    cola = cola_misiones.get(personaje_id)
    if cola is None:
        raise HTTPException(status_code=404, detail="Este personaje no tiene misiones activas")

    misiones = []
    for m_id in cola.items:
        mision = db.query(models.Mision).get(m_id)
        if mision:
            misiones.append(mision.descripcion)
    return misiones

#python -m uvicorn main:app --reload
#python -m uvicorn main:app --reload --debug
