#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================
PHOTOBOOTH APPLICATION - MAIN ENTRY POINT
==========================================
File chính để khởi động ứng dụng Photobooth (chế độ có thanh toán)

Chức năng:
- Khởi tạo QApplication
- Load cấu hình hệ thống
- Khởi động giao diện PhotoboothApp

Cách chạy:
    python main_app.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont

# Import config và utils
from config.settings import load_config
from modules.utils import ensure_directories

# Import giao diện chính
from ui.ui_main import PhotoboothApp


def main():
    """
    Hàm main - Entry point của ứng dụng
    """
    # 1. Kiểm tra config.json
    if not load_config():
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "❌ Thiếu cấu hình",
            "Không tìm thấy file config.json!\n\n"
            "Vui lòng chạy setup_admin.py trước để tạo cấu hình."
        )
        sys.exit(1)
    
    # 2. Đảm bảo thư mục tồn tại  
    ensure_directories()
    
    # 3. Tạo QApplication
    app = QApplication(sys.argv)
    
    # 4. Set font mặc định - sử dụng font hỗ trợ tiếng Việt
    font = QFont("Arial", 12)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    # 5. Khởi tạo và hiển thị cửa sổ chính
    window = PhotoboothApp()
    window.show()
    
    # 6. Chạy ứng dụng
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
