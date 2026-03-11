# ==========================================
# IMAGE SERVICE PACKAGE
# ==========================================
"""
Service xử lý ảnh, được tách từ modules/image_processing/processor.py.

Sub-modules:
  - collage.py   → Tạo collage từ nhiều ảnh
  - template.py  → Load, detect, overlay template
  - filters.py   → Apply filter lên ảnh
"""

from src.services.image.collage import create_collage, crop_to_aspect_wh
from src.services.image.template import (
    generate_frame_templates,
    load_templates_for_layout,
    load_all_templates_for_group,
    detect_layout_from_template,
    apply_template_overlay,
)
