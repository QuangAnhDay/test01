# ==========================================
# IMAGE PROCESSOR (BACKWARD-COMPATIBLE RE-EXPORT)
# ==========================================
"""
File này giữ lại để backward-compatible.
Tất cả function đã được tách ra các module riêng trong src/services/image/.

Các module mới:
  - src.services.image.collage   → create_collage, crop_to_aspect_wh
  - src.services.image.template  → generate_frame_templates, load_templates_for_layout, 
                                    load_all_templates_for_group, detect_layout_from_template,
                                    apply_template_overlay
  - src.services.image.filters   → apply_filter, get_available_filters
"""

# Re-export tất cả để code cũ không bị lỗi
from src.services.image.collage import create_collage, crop_to_aspect_wh

from src.services.image.template import (
    generate_frame_templates,
    load_templates_for_layout,
    load_all_templates_for_group,
    detect_layout_from_template,
    apply_template_overlay,
)

from src.services.image.filters import apply_filter, get_available_filters
