# ==========================================
# QR CODE UTILITIES
# ==========================================
"""
Tạo và xử lý mã QR.
"""

import qrcode
from io import BytesIO
from PyQt5.QtGui import QImage, QPixmap


def generate_qr_code(content, size=300):
    """Tạo mã QR từ nội dung."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((size, size))

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    q_img = QImage()
    q_img.loadFromData(buffer.getvalue())
    return QPixmap.fromImage(q_img)
