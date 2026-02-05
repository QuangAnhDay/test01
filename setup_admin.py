#!/usr/bin/env python
"""
Shortcut để chạy Admin Setup từ thư mục gốc.
Chạy bằng lệnh: python setup_admin.py
"""
import sys
import os

# Thêm đường dẫn gốc
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# Import và chạy AdminSetup
from config.admin_setup import AdminSetup
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminSetup()
    window.show()
    sys.exit(app.exec_())
