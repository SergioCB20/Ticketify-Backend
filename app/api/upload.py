from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
from pathlib import Path
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

# Configuración
UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".wmv", ".webm"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

# Crear directorio de uploads si no existe
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "images").mkdir(exist_ok=True)
(UPLOAD_DIR / "videos").mkdir(exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Obtener la extensión del archivo"""
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para el archivo"""
    extension = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{extension}"


def validate_image(file: UploadFile) -> None:
    """Validar que el archivo sea una imagen válida"""
    extension = get_file_extension(file.filename)
    
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de imagen no válido. Formatos permitidos: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Verificar tamaño (esto es aproximado, el tamaño real se verifica al leer)
    if file.size and file.size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"La imagen es muy grande. Tamaño máximo: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )


def validate_video(file: UploadFile) -> None:
    """Validar que el archivo sea un video válido"""
    extension = get_file_extension(file.filename)
    
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de video no válido. Formatos permitidos: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
    
    if file.size and file.size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"El video es muy grande. Tamaño máximo: {MAX_VIDEO_SIZE / 1024 / 1024}MB"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subir una imagen
    
    - **file**: Archivo de imagen (JPG, PNG, GIF, WEBP)
    - Tamaño máximo: 5MB
    - Requiere autenticación
    """
    try:
        # Validar imagen
        validate_image(file)
        
        # Generar nombre único
        unique_filename = generate_unique_filename(file.filename)
        file_path = UPLOAD_DIR / "images" / unique_filename
        
        # Guardar archivo
        contents = await file.read()
        
        # Verificar tamaño real
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"La imagen es muy grande. Tamaño máximo: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Construir URL
        file_url = f"/uploads/images/{unique_filename}"
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Imagen subida exitosamente",
                "filename": unique_filename,
                "url": file_url,
                "size": len(contents)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subir un video
    
    - **file**: Archivo de video (MP4, AVI, MOV, WMV, WEBM)
    - Tamaño máximo: 50MB
    - Requiere autenticación
    """
    try:
        # Validar video
        validate_video(file)
        
        # Generar nombre único
        unique_filename = generate_unique_filename(file.filename)
        file_path = UPLOAD_DIR / "videos" / unique_filename
        
        # Guardar archivo
        contents = await file.read()
        
        # Verificar tamaño real
        if len(contents) > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"El video es muy grande. Tamaño máximo: {MAX_VIDEO_SIZE / 1024 / 1024}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Construir URL
        file_url = f"/uploads/videos/{unique_filename}"
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Video subido exitosamente",
                "filename": unique_filename,
                "url": file_url,
                "size": len(contents)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir video: {str(e)}")


@router.post("/multimedia")
async def upload_multimedia(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subir múltiples archivos multimedia (imágenes y videos)
    
    - **files**: Lista de archivos
    - Máximo 10 archivos por solicitud
    - Requiere autenticación
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="No se pueden subir más de 10 archivos a la vez"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            extension = get_file_extension(file.filename)
            
            # Determinar si es imagen o video
            if extension in ALLOWED_IMAGE_EXTENSIONS:
                validate_image(file)
                subfolder = "images"
                max_size = MAX_IMAGE_SIZE
            elif extension in ALLOWED_VIDEO_EXTENSIONS:
                validate_video(file)
                subfolder = "videos"
                max_size = MAX_VIDEO_SIZE
            else:
                errors.append({
                    "filename": file.filename,
                    "error": "Formato no soportado"
                })
                continue
            
            # Generar nombre único
            unique_filename = generate_unique_filename(file.filename)
            file_path = UPLOAD_DIR / subfolder / unique_filename
            
            # Guardar archivo
            contents = await file.read()
            
            if len(contents) > max_size:
                errors.append({
                    "filename": file.filename,
                    "error": f"Archivo muy grande (máx: {max_size / 1024 / 1024}MB)"
                })
                continue
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Agregar a lista de subidos
            uploaded_files.append({
                "original_filename": file.filename,
                "filename": unique_filename,
                "url": f"/uploads/{subfolder}/{unique_filename}",
                "type": "image" if subfolder == "images" else "video",
                "size": len(contents)
            })
        
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return JSONResponse(
        status_code=201 if uploaded_files else 400,
        content={
            "message": f"{len(uploaded_files)} archivo(s) subido(s) exitosamente",
            "uploaded": uploaded_files,
            "errors": errors if errors else None
        }
    )


@router.delete("/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar un archivo multimedia
    
    - **filename**: Nombre del archivo a eliminar
    - Requiere autenticación
    """
    try:
        # Buscar archivo en imágenes o videos
        image_path = UPLOAD_DIR / "images" / filename
        video_path = UPLOAD_DIR / "videos" / filename
        
        if image_path.exists():
            os.remove(image_path)
            return {"message": "Imagen eliminada exitosamente"}
        elif video_path.exists():
            os.remove(video_path)
            return {"message": "Video eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")
