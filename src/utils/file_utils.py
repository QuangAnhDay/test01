# ==========================================
# FILE UTILITIES
# ==========================================
"""
Quản lý thư mục, tạo dữ liệu mẫu, load ảnh.
"""

import os
import cv2
import numpy as np
from src.shared.types.models import TEMPLATE_DIR, OUTPUT_DIR, SAMPLE_PHOTOS_DIR


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
    
    # Nạp font
    from src.utils.font_loader import load_application_fonts
    load_application_fonts()


def create_sample_templates():
    """Tạo các template mẫu."""
    width, height = 1280, 720

    test_dir = os.path.join(TEMPLATE_DIR, "vertical")
    os.makedirs(test_dir, exist_ok=True)

    # Template 1: Khung đỏ đơn giản
    img = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img, (0, 0), (width, height), (0, 0, 255, 255), 40)
    cv2.putText(img, "PHOTOBOOTH", (width // 2 - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img[80:height - 40, 40:width - 40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(test_dir, "frame_red_test.png"), img)

    # Template 2: Khung xanh
    img2 = np.zeros((height, width, 4), dtype=np.uint8)
    cv2.rectangle(img2, (0, 0), (width, height), (255, 100, 0, 255), 40)
    cv2.putText(img2, "MEMORIES", (width // 2 - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 4)
    img2[80:height - 40, 40:width - 40] = [0, 0, 0, 0]
    cv2.imwrite(os.path.join(test_dir, "frame_blue_test.png"), img2)


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
        for y in range(400):
            ratio = y / 400
            img[y, :] = (
                int(color[0] * (1 - ratio * 0.5)),
                int(color[1] * (1 - ratio * 0.5)),
                int(color[2] * (1 - ratio * 0.5))
            )
        cv2.putText(img, text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Sample", (80, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imwrite(os.path.join(SAMPLE_PHOTOS_DIR, f"sample_{i + 1}.jpg"), img)


def load_sample_photos():
    """Load các ảnh mẫu từ thư mục."""
    photos = []
    if os.path.exists(SAMPLE_PHOTOS_DIR):
        for f in sorted(os.listdir(SAMPLE_PHOTOS_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(SAMPLE_PHOTOS_DIR, f))
    if os.path.exists(OUTPUT_DIR):
        for f in sorted(os.listdir(OUTPUT_DIR)):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                photos.append(os.path.join(OUTPUT_DIR, f))
    return photos
