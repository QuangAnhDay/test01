import qrcode
from io import BytesIO
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def generate_qr_code(data, size=300):
    """Tạo QPixmap QR Code từ dữ liệu."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Chuyển đổi sang QPixmap
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    pixmap = QPixmap()
    pixmap.loadFromData(buffer.getvalue())
    
    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
