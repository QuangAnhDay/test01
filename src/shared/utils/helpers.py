# ==========================================
# HÀM TIỆN ÍCH (BACKWARD-COMPATIBLE RE-EXPORT)
# ==========================================
"""
File này giữ lại để backward-compatible.
Tất cả function đã được tách ra các module riêng trong src/utils/.
Import từ đây vẫn hoạt động bình thường.

Các module mới:
  - src.utils.image_helpers  → get_rounded_pixmap, overlay_images, convert_cv_qt, crop_to_aspect
  - src.utils.file_utils     → ensure_directories, load_sample_photos, create_sample_*
  - src.utils.font_loader    → load_application_fonts
  - src.utils.system_check   → check_printer_available
"""

# Re-export tất cả để code cũ không bị lỗi
from src.utils.image_helpers import (
    get_rounded_pixmap,
    overlay_images,
    convert_cv_qt,
    crop_to_aspect,
)

from src.utils.file_utils import (
    ensure_directories,
    load_sample_photos,
    create_sample_templates,
    create_sample_photos,
)

from src.utils.font_loader import load_application_fonts

from src.utils.system_check import check_printer_available
