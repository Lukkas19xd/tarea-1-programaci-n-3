from sqlalchemy import Column, Integer, String
from database import Base

class Vuelo(Base):
    __tablename__ = "vuelos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, index=True)
    destino = Column(String)
    prioridad = Column(String)  # emergencia / normal / demorado
