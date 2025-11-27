import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.qr_generator import generate_qr_image, generate_ticket_qr_data
from app.utils.imgbb_upload import upload_qr_to_imgbb

print("⏳ Generando QR real...")

payload = generate_ticket_qr_data("test-ticket-123", "fake-event-999")
qr_b64 = generate_qr_image(payload)

print("⏳ Subiéndolo a ImgBB...")

url = upload_qr_to_imgbb(qr_b64)

print("\nResultado:\n", url)

