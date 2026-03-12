# ==========================================
# IMAGE WORKFLOW - Quy trình tạo sản phẩm cuối
# ==========================================
"""
Xử lý các bước sau khi chụp xong:
1. Tạo collage từ danh sách ảnh.
2. Áp dụng template (nếu có).
3. Save file.
4. Thông báo hoàn tất.
"""

import os
import cv2
from PyQt5.QtCore import QObject, pyqtSignal
from src.services.image.collage import create_collage
from src.services.image.template import apply_template_overlay
from src.shared.types.models import OUTPUT_DIR, generate_unique_code


class ImageWorkflow(QObject):
    """Quản lý quy trình xử lý ảnh sau khi chụp."""
    processing_finished = pyqtSignal(str, object) # path, image_data

    def __init__(self):
        super().__init__()

    def process_final_image(self, captured_photos, layout_type, template_path=None):
        """Thực hiện tạo collage và overlay template."""
        try:
            # 1. Tạo Collage
            collage = create_collage(captured_photos, layout_type)
            
            # 2. Áp dụng Template (nếu có)
            if template_path and os.path.exists(template_path):
                final_img = apply_template_overlay(collage, template_path)
            else:
                final_img = collage
            
            # 3. Thông báo (Bỏ bước cv2.imwrite để không lưu file cục bộ)
            save_path = "memory_buffer"  # Dummy path for compatibility
            
            self.processing_finished.emit(save_path, final_img)
            return save_path, final_img
        except Exception as e:
            print(f"[IMAGE WORKFLOW ERROR] {e}")
            return None, None
