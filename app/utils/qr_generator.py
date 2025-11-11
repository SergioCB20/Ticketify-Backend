"""
QR Code Generator Utility
Genera códigos QR visuales como imágenes en formato base64
"""
import qrcode
from io import BytesIO
import base64
from typing import Optional


def generate_qr_image(data: str, size: int = 10, border: int = 2) -> str:
    """
    Genera un código QR visual como imagen en formato base64.
    
    Args:
        data: Información a codificar en el QR (ej: ticket_id, url de validación)
        size: Tamaño del QR (default: 10 = 370x370 px aprox)
        border: Grosor del borde (default: 2)
    
    Returns:
        String en formato base64 de la imagen PNG del QR
        Formato: "data:image/png;base64,iVBORw0KGgo..."
    """
    try:
        # Crear objeto QR con configuración
        qr = qrcode.QRCode(
            version=1,  # Tamaño del QR (1 = más pequeño, 40 = más grande)
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Máxima corrección de errores
            box_size=size,  # Tamaño de cada "caja" del QR
            border=border,  # Grosor del borde blanco
        )
        
        # Agregar datos al QR
        qr.add_data(data)
        qr.make(fit=True)
        
        # Crear la imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir la imagen a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Codificar en base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Retornar con el prefijo data URL
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"Error generando QR: {e}")
        # En caso de error, retornar un QR simple con texto
        return f"QR_ERROR_{data}"


def generate_ticket_qr_data(ticket_id: str, event_id: str) -> str:
    """
    Genera el contenido que irá dentro del QR del ticket.
    Puede ser una URL de validación o un JSON con información del ticket.
    
    Args:
        ticket_id: UUID del ticket
        event_id: UUID del evento
    
    Returns:
        String con el contenido del QR (puede ser URL o JSON)
    """
    # Opción 1: URL de validación (recomendado para escaneo rápido)
    # return f"https://ticketify.com/validate/{ticket_id}"
    
    # Opción 2: JSON con información del ticket (más información pero más grande)
    import json
    qr_data = {
        "ticket_id": ticket_id,
        "event_id": event_id,
        "type": "TICKET_VALIDATION"
    }
    return json.dumps(qr_data)
