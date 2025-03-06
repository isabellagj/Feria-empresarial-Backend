from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Optional
import datetime

class RegistroCreate(BaseModel):
    nit: str = Field(..., min_length=3)
    nombre_empresa: str = Field(..., min_length=3, max_length=100)
    email_contacto: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    telefono_contacto: str = Field(..., pattern=r'^\d{10}$')
    datos_registro: Dict

class Registro(BaseModel):
    id: int
    nit: str
    nombre_empresa: str
    email_contacto: str
    telefono_contacto: str
    estado: str
    fecha_registro: datetime.datetime
    datos_registro: Dict
    ruta_certificado: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True