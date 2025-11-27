import base64
import requests
from app.core.config import settings
IMGBB_API_KEY = "4a4c6297ec8c2bae0f34707c911f32a6"  # tu API key


def upload_qr_to_imgbb(qr_base64: str) -> str:
    """
    Sube un QR en base64 a ImgBB y devuelve la URL pública.
    Acepta formatos tipo: "data:image/png;base64,AAAA...."
    """

    try:
        # limpiar "data:image/png;base64,"
        if "," in qr_base64:
            qr_base64 = qr_base64.split(",")[1]

        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": qr_base64
        }

        res = requests.post(url, data=payload, timeout=10)
        data = res.json()

        # Validación
        if not data.get("success"):
            print("❌ Error subiendo a ImgBB:", data)
            return None

        # URL directa del PNG
        return data["data"]["url"]

    except Exception as e:
        print("❌ Excepción al subir a ImgBB:", str(e))
        return None
