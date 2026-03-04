import os
import sys

# FIX PATH: Tìm thư mục gốc của dự án
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from PyQt5.QtWidgets import QApplication
    from src.admin.pages.settings import CameraSetupApp

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        # Khởi tạo class cấu hình camera
        window = CameraSetupApp()
        window.show()
        sys.exit(app.exec_())
except Exception as e:
    print(f"Loi khoi chay: {e}")
    import traceback
    traceback.print_exc()
    input("\nNhan Enter de thoat...")
