# ==========================================
# FONT LOADER
# ==========================================
"""
Nạp font từ thư mục public/fonts cho ứng dụng.
"""

import os
from PyQt5.QtGui import QFontDatabase


def load_application_fonts():
    """Nạp tất cả font từ thư mục public/fonts."""
    from src.config import PROJECT_ROOT
    fonts_dir = os.path.join(PROJECT_ROOT, "public", "fonts")
    
    if os.path.exists(fonts_dir):
        for f in os.listdir(fonts_dir):
            if f.lower().endswith(('.ttf', '.otf')):
                font_path = os.path.join(fonts_dir, f)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"[FONT] Loaded: {f} (Family: {families})")
                else:
                    print(f"[FONT ERROR] Failed to load: {f}")
    else:
        print(f"[FONT] Fonts directory not found: {fonts_dir}")
