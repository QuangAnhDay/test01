# ==========================================
# HÀM TIỆN ÍCH (UTILITY FUNCTIONS)
# ==========================================
"""
File này chứa các hàm hỗ trợ xử lý ảnh, hệ thống và các tiện ích khác.
"""

import os
import cv2
import numpy as np
import subprocess
import qrcode
from io import BytesIO
from PyQt5.QtGui import QImage, QPixmap
from configs import TEMPLATE_DIR, OUTPUT_DIR, SAMPLE_PHOTOS_DIR


# ==========================================
# QUẢN LÝ THƯ MỤC
# ==========================================

def ensure_directories():
    """Tạo các thư mục cần thiết."""
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
        create_sample_templates()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(SAMPLE_PHOTOS_DIR):
        os.makedirs(SAMPLE_PHOTOS_DIR)
        create_sample_photos()


# ==========================================
# TẠO DỮ LIỆU MẪU
# ==========================================

def create_sample_templates():
    """Tạo các template mẫu."""
    width, height = 1280, 720
    
    # Template 1: Khung đỏ đơn giản
    img = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (width, height), (0, 0, 255, 255), 40)
    cv2.putText(img, "PHOTOBOOTH", (width//2 - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img[80:height-40, 40:width-40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(TEMPLATE_DIR, "frame_red.png"), img)
    
    # Template 2: Khung xanh
    img2 = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img2, (0, 0), (width, height), (255, 100, 0, 255), 40)
    cv2.putText(img2, "MEMORIES", (width//2 - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img2[80:height-40, 40:width-40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(TEMPLATE_DIR, "frame_blue.png"), img2)


def create_sample_photos():
    """Tạo các ảnh mẫu demo."""
    colors = [
        ((255, 100, 150), "Memory 1"),
        ((100, 200, 255), "Memory 2"),
        ((150, 255, 150), "Memory 3"),
        ((255, 200, 100), "Memory 4"),
        ((200, 150, 255), "Memory 5"),
        ((100, 255, 200), "Memory 6"),
        ((255, 150, 200), "Memory 7"),
        ((150, 200, 255), "Memory 8"),
    ]
    
    for i, (color, text) in enumerate(colors):
        img = np.zeros((400, 300, 3), dtype=np.uint8)
        # Gradient background
        for y in range(400):
            ratio = y / 400
            img[y, :] = (
                int(color[0] * (1 - ratio * 0.5)),
                int(color[1] * (1 - ratio * 0.5)),
                int(color[2] * (1 - ratio * 0.5))
            )
        # Add text
        cv2.putText(img, text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Sample", (80, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(os.path.join(SAMPLE_PHOTOS_DIR, f"sample_{i+1}.jpg"), img)


def load_sample_photos():
    """Load các ảnh mẫu từ thư mục."""
    photos = []
    if os.path.exists(SAMPLE_PHOTOS_DIR):
        for f in sorted(os.listdir(SAMPLE_PHOTOS_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(SAMPLE_PHOTOS_DIR, f))
    # Load từ output nếu có
    if os.path.exists(OUTPUT_DIR):
        for f in sorted(os.listdir(OUTPUT_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(OUTPUT_DIR, f))
    return photos


# ==========================================
# XỬ LÝ ẢNH
# ==========================================

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
    
    # Convert PIL Image to QPixmap
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    q_img = QImage()
    q_img.loadFromData(buffer.getvalue())
    return QPixmap.fromImage(q_img)


def overlay_images(background, foreground):
    """Ghép ảnh foreground (có alpha) lên background."""
    bg_h, bg_w = background.shape[:2]
    fg_h, fg_w = foreground.shape[:2]

    if (bg_w, bg_h) != (fg_w, fg_h):
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
    """Chuyển đổi ảnh OpenCV sang QPixmap."""
    if cv_img is None:
        return QPixmap()
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_format)


def crop_to_aspect(img, target_ratio=1.5):
    """
    Cắt ảnh theo tỷ lệ khung hình mong muốn (3:2 = 1.5).
    
    Args:
        img: Ảnh OpenCV (numpy array)
        target_ratio: Tỷ lệ width/height mong muốn (mặc định 1.5 cho 3:2)
    
    Returns:
        Ảnh đã được cắt theo tỷ lệ
    """
    h, w = img.shape[:2]
    current_ratio = w / h
    
    if abs(current_ratio - target_ratio) < 0.01:
        return img
    
    if current_ratio > target_ratio:
        # Ảnh quá rộng, cắt 2 bên
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        return img[:, start_x:start_x + new_w]
    else:
        # Ảnh quá cao, cắt trên dưới
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        return img[start_y:start_y + new_h, :]


# ==========================================
# KIỂM TRA HỆ THỐNG
# ==========================================

def check_printer_available():
    """Kiểm tra xem có máy in nào được kết nối không (Windows)."""
    if os.name != 'nt':
        return False, "Chỉ hỗ trợ Windows"
    
    try:
        # Dùng PowerShell để lấy danh sách máy in
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Printer | Select-Object -ExpandProperty Name'],
            capture_output=True, text=True, timeout=5
        )
        printers = result.stdout.strip().split('\n')
        printers = [p.strip() for p in printers if p.strip()]
        
        if printers:
            return True, printers[0]  # Trả về máy in đầu tiên
        else:
            return False, "Không tìm thấy máy in"
    except Exception as e:
        return False, str(e)
