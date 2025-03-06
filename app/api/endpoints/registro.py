from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import registro as schemas
from app.models.registro import RegistroFeria
from sqlalchemy.exc import IntegrityError
import json
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "C:/Users/Sergio/Desktop/feria-empresarial/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=schemas.Registro)
async def crear_registro(
    *,
    db: Session = Depends(deps.get_db),
    datos_registro: str = Form(...),
    certificado_manipulacion: UploadFile = File(None)
):
    """
    Crear nuevo registro de empresa para la feria.
    """
    try:
        datos = json.loads(datos_registro)
        
        registro_data = {
            "nit": datos.get("nit", ""),
            "nombre_empresa": datos["nombre_empresa"],
            "email_contacto": datos["email_contacto"],
            "telefono_contacto": datos["telefono_contacto"],
            "datos_registro": datos
        }

        registro_in = schemas.RegistroCreate(**registro_data)

        ruta_certificado = None
        if certificado_manipulacion:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = os.path.splitext(certificado_manipulacion.filename)[1]
            nombre_archivo = f"{registro_data['nit']}_{timestamp}{extension}"
            ruta_archivo = os.path.join(UPLOAD_DIR, nombre_archivo)
            
            with open(ruta_archivo, "wb+") as file_object:
                file_object.write(await certificado_manipulacion.read())
            
            ruta_certificado = ruta_archivo

        registro = RegistroFeria(
            nit=registro_in.nit,
            nombre_empresa=registro_in.nombre_empresa,
            email_contacto=registro_in.email_contacto,
            telefono_contacto=registro_in.telefono_contacto,
            datos_registro=registro_in.datos_registro,
            ruta_certificado=ruta_certificado
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al procesar los datos del formulario"
        )
    except IntegrityError:
        db.rollback()
        if ruta_certificado and os.path.exists(ruta_certificado):
            os.remove(ruta_certificado)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa registrada con este NIT"
        )
    except Exception as e:
        if ruta_certificado and os.path.exists(ruta_certificado):
            os.remove(ruta_certificado)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/", response_model=List[schemas.Registro])
def listar_registros(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    estado: str = None
):
    """
    Obtener lista de registros con paginación y filtros.
    """
    query = db.query(RegistroFeria)
    if estado:
        query = query.filter(RegistroFeria.estado == estado)
    
    registros = query.offset(skip).limit(limit).all()
    return registros

@router.get("/{registro_id}", response_model=schemas.Registro)
def obtener_registro(
    *,
    db: Session = Depends(deps.get_db),
    registro_id: int
):
    """
    Obtener un registro específico por ID.
    """
    registro = db.query(RegistroFeria).filter(RegistroFeria.id == registro_id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro no encontrado"
        )
    return registro

@router.patch("/{registro_id}/estado")
def actualizar_estado(
    *,
    db: Session = Depends(deps.get_db),
    registro_id: int,
    estado: str
):
    """
    Actualizar el estado de un registro.
    """
    estados_validos = ['pendiente', 'aprobado', 'rechazado']
    if estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {estados_validos}"
        )

    registro = db.query(RegistroFeria).filter(RegistroFeria.id == registro_id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro no encontrado"
        )
    
    registro.estado = estado
    db.commit()
    db.refresh(registro)
    return {"message": "Estado actualizado exitosamente"}

@router.get("/estadisticas/resumen")
def obtener_estadisticas(db: Session = Depends(deps.get_db)):
    """
    Obtener estadísticas generales de los registros.
    """
    total_registros = db.query(RegistroFeria).count()
    registros_por_estado = db.query(
        RegistroFeria.estado,
        func.count(RegistroFeria.id)
    ).group_by(RegistroFeria.estado).all()
   
    sectores = db.query(
        func.json_extract_path_text(RegistroFeria.datos_registro, 'datos_registro', 'sector'),
        func.count(RegistroFeria.id)
    ).group_by(
        func.json_extract_path_text(RegistroFeria.datos_registro, 'datos_registro', 'sector')
    ).all()
   
    return {
        "total_registros": total_registros,
        "por_estado": dict(registros_por_estado),
        "por_sector": dict(sectores)
    }