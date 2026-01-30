# ==========================================
# MAIN ENTRY POINT
# ==========================================
"""
File chạy chính của ứng dụng Photobooth.
Chạy file này để khởi động ứng dụng: python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from configs import load_config
from utils import ensure_directories
from main_app import PhotoboothApp  # Tạm thời import từ main_app.py


def main():
    """Hàm main - Entry point của ứng dụng."""
    
    # Tạo QApplication
    app = QApplication(sys.argv)
    
    # Đảm bảo các thư mục cần thiết tồn tại
    ensure_directories()
    
    # Kiểm tra và load config
    if not load_config():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Thiếu cấu hình")
        msg.setText("Không tìm thấy file config.json")
        msg.setInformativeText(
            "Vui lòng tạo file config.json theo mẫu config.example.json\n"
            "và điền đầy đủ thông tin cấu hình."
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return 1
    
    # Tạo và hiển thị cửa sổ chính
    window = PhotoboothApp()
    window.show()
    
    # Chạy ứng dụng
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
