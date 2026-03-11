# ==========================================
# FILTERS SERVICE - Bộ lọc ảnh
# ==========================================
"""
Chịu trách nhiệm: Áp dụng các hiệu ứng filter lên ảnh.
Sẽ được mở rộng khi tích hợp tính năng filter vào app.
"""

import cv2
import numpy as np


def apply_filter(image, filter_name):
    """Áp dụng filter lên ảnh OpenCV (BGR).
    
    Args:
        image: numpy array (BGR)
        filter_name: tên filter (str)
    
    Returns:
        numpy array (BGR) đã áp dụng filter
    """
    if image is None or filter_name == "none":
        return image
    
    filters = {
        "grayscale": _filter_grayscale,
        "sepia": _filter_sepia,
        "warm": _filter_warm,
        "cool": _filter_cool,
        "vintage": _filter_vintage,
    }
    
    func = filters.get(filter_name)
    if func:
        return func(image)
    return image


def get_available_filters():
    """Trả về danh sách tên filter có sẵn."""
    return ["none", "grayscale", "sepia", "warm", "cool", "vintage"]


def _filter_grayscale(img):
    """Chuyển ảnh sang trắng đen."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _filter_sepia(img):
    """Áp dụng hiệu ứng sepia (nâu cổ điển)."""
    kernel = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189]
    ])
    sepia = cv2.transform(img, kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)


def _filter_warm(img):
    """Tăng tone ấm (vàng/cam)."""
    result = img.copy().astype(np.float32)
    result[:, :, 2] = np.clip(result[:, :, 2] * 1.1 + 10, 0, 255)  # Red
    result[:, :, 1] = np.clip(result[:, :, 1] * 1.05, 0, 255)       # Green
    result[:, :, 0] = np.clip(result[:, :, 0] * 0.9, 0, 255)        # Blue
    return result.astype(np.uint8)


def _filter_cool(img):
    """Tăng tone lạnh (xanh dương)."""
    result = img.copy().astype(np.float32)
    result[:, :, 0] = np.clip(result[:, :, 0] * 1.1 + 10, 0, 255)  # Blue
    result[:, :, 2] = np.clip(result[:, :, 2] * 0.9, 0, 255)        # Red
    return result.astype(np.uint8)


def _filter_vintage(img):
    """Hiệu ứng vintage (giảm contrast, thêm vignette nhẹ)."""
    # Giảm contrast
    result = cv2.convertScaleAbs(img, alpha=0.85, beta=30)
    # Thêm tone sepia nhẹ
    sepia = _filter_sepia(result)
    result = cv2.addWeighted(result, 0.6, sepia, 0.4, 0)
    return result
