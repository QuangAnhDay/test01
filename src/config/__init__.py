# ==========================================
# CONFIG PATH RESOLVER
# ==========================================
"""
Module trung tâm quản lý đường dẫn tới các file config.
Tất cả các file khác nên import từ đây thay vì hardcode path.

Hỗ trợ backward-compatible: Nếu file nằm ở root (cũ) thì vẫn đọc được,
nhưng ưu tiên đọc từ config/ (mới).
"""

import os

# Project root (thư mục chứa src/, config/, assets/...)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Hàm tìm file config với fallback ---
def _resolve_config_path(filename, new_name=None):
    """
    Tìm file config theo thứ tự ưu tiên:
    1. config/<new_name>  (cấu trúc mới)
    2. config/<filename>  (cấu trúc mới, tên cũ)
    3. <filename>          (root, backward-compatible)
    """
    candidates = []
    if new_name:
        candidates.append(os.path.join(_PROJECT_ROOT, "config", new_name))
    candidates.append(os.path.join(_PROJECT_ROOT, "config", filename))
    candidates.append(os.path.join(_PROJECT_ROOT, filename))
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    # Trả về đường dẫn mới (ưu tiên ghi vào config/)
    if new_name:
        return os.path.join(_PROJECT_ROOT, "config", new_name)
    return os.path.join(_PROJECT_ROOT, "config", filename)


# --- Đường dẫn config chuẩn ---
APP_CONFIG_PATH = _resolve_config_path("config.json", "app_config.json")
CAMERA_SETTINGS_PATH = _resolve_config_path("camera_settings.json")
CUSTOM_LAYOUTS_PATH = _resolve_config_path("custom_layouts.json")

# --- Đường dẫn thư mục assets ---
ASSETS_DIR = os.path.join(_PROJECT_ROOT, "assets")
TEMPLATES_DIR = os.path.join(_PROJECT_ROOT, "templates")
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")
SAMPLE_PHOTOS_DIR = os.path.join(_PROJECT_ROOT, "sample_photos")

# Public dir (backward-compatible, sẽ migrate sang assets/ ở Phase sau)
PUBLIC_DIR = os.path.join(_PROJECT_ROOT, "public")

# Project root export
PROJECT_ROOT = _PROJECT_ROOT
