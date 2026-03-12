# ==========================================
# UTILITIES PACKAGE
# ==========================================
"""
Các tiện ích thuần túy, không phụ thuộc vào business logic.
"""
from src.utils.file_utils import ensure_directories, load_sample_photos
from src.utils.font_loader import load_application_fonts
from src.utils.system_check import check_printer_available
from src.utils.image_helpers import (
    get_rounded_pixmap, overlay_images, convert_cv_qt, crop_to_aspect
)
from src.utils.qr_utils import generate_qr_code
