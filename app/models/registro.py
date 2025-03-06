from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class RegistroFeria(Base):
    __tablename__ = "registros_feria"

    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String, unique=True, nullable=False, index=True)
    nombre_empresa = Column(String, nullable=False)
    email_contacto = Column(String, nullable=False)
    telefono_contacto = Column(String, nullable=False)
    estado = Column(String, default='pendiente', index=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    datos_registro = Column(JSON, nullable=False)
    ruta_certificado = Column(String, nullable=True)