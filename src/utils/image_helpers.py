# ==========================================
# IMAGE HELPERS (Qt + OpenCV conversion)
# ==========================================
"""
Các hàm xử lý ảnh liên quan đến Qt:
- Chuyển đổi OpenCV ↔ QPixmap/QImage
- Bo tròn góc pixmap
- Overlay ảnh
- Crop tỷ lệ khung hình
"""

import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPainterPath
from PyQt5.QtCore import Qt


def get_rounded_pixmap(input_data, radius=24):
    """Tạo pixmap với các góc bo tròn (clipping)."""
    if input_data.isNull():
        return input_data
        
    # Chuyển đổi sang QPixmap nếu đầu vào là QImage để vẽ đồng nhất
    if isinstance(input_data, QImage):
        pixmap = QPixmap.fromImage(input_data)
    else:
        pixmap = input_data

    size = pixmap.size()
    # Tạo QImage mới với alpha channel (Sử dụng FORMAT_ARGB32_Premultiplied để có chất lượng tốt)
    image = QImage(size.width(), size.height(), QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    
    # Vẽ pixmap lên image với mask bo góc
    painter = QPainter(image)
    if not painter.isActive():
        # Phải bảo đảm painter được khởi tạo thành công
        if not painter.begin(image):
            return QPixmap()

    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    # Tạo path bo góc
    path = QPainterPath()
    path.addRoundedRect(0, 0, float(size.width()), float(size.height()), float(radius), float(radius))
    painter.setClipPath(path)
    
    # Vẽ pixmap vào image
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    
    return QPixmap.fromImage(image)


def overlay_images(background, foreground):
    """Ghép ảnh foreground (có alpha) lên background."""
    bg_h, bg_w = background.shape[:2]
    fg_h, fg_w = foreground.shape[:2]

    if (bg_w, bg_h) != (fg_w, fg_h):
        print(f"[WARNING] overlay_images: kích thước khác nhau! Background={bg_w}x{bg_h}, Template={fg_w}x{fg_h} → resize template")
        foreground = cv2.resize(foreground, (bg_w, bg_h))

    if foreground.shape[2] < 4:
        return background

    alpha = foreground[:, :, 3] / 255.0
    output = np.zeros_like(background)

    for c in range(0, 3):
        output[:, :, c] = (foreground[:, :, c] * alpha +
                           background[:, :, c] * (1.0 - alpha))

    return output


def convert_cv_qt(cv_img):
    """Chuyển đổi ảnh OpenCV sang QPixmap an toàn."""
    if cv_img is None:
        return QPixmap()
    # Sử dụng BGRA cho ARGB32 để có hiệu năng tốt nhất trên Win
    bgra_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2BGRA)
    h, w, ch = bgra_image.shape
    bytes_per_line = ch * w
    qt_image = QImage(bgra_image.data, w, h, bytes_per_line, QImage.Format_ARGB32).copy()
    return QPixmap.fromImage(qt_image)


def crop_to_aspect(img, target_ratio=1.5):
    """
    Cắt ảnh theo tỷ lệ khung hình mong muốn (3:2 = 1.5).
    """
    h, w = img.shape[:2]
    current_ratio = w / h

    if abs(current_ratio - target_ratio) < 0.01:
        return img

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        return img[:, start_x:start_x + new_w]
    else:
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        return img[start_y:start_y + new_h, :]
