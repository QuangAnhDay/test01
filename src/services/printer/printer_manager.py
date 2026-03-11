# ==========================================
# PRINTER MANAGER - Xử lý lệnh in
# ==========================================
"""
Module quản lý máy in: kiểm tra kết nối, gửi lệnh in.
"""

import os
import subprocess


class PrinterManager:
    """Quản lý kết nối và điều khiển máy in."""

    def __init__(self):
        self.available = False
        self.printer_name = ""
        self.check_connection()

    def check_connection(self):
        """Kiểm tra xem có máy in nào được kết nối không (Windows)."""
        if os.name != 'nt':
            self.available = False
            self.printer_name = "Chỉ hỗ trợ Windows"
            return False

        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Printer | Select-Object -ExpandProperty Name'],
                capture_output=True, text=True, timeout=5
            )
            printers = result.stdout.strip().split('\n')
            printers = [p.strip() for p in printers if p.strip()]

            if printers:
                self.available = True
                self.printer_name = printers[0]
                return True
            else:
                self.available = False
                self.printer_name = "Không tìm thấy máy in"
                return False
        except Exception as e:
            self.available = False
            self.printer_name = str(e)
            return False

    def print_image(self, image_path):
        """Gửi lệnh in ảnh."""
        if not self.available:
            return False, "Không có máy in khả dụng"

        if not os.path.exists(image_path):
            return False, f"File không tồn tại: {image_path}"

        try:
            # Sử dụng lệnh in mặc định của Windows
            os.startfile(image_path, "print")
            return True, f"Đã gửi lệnh in tới {self.printer_name}"
        except Exception as e:
            return False, str(e)

    def get_status(self):
        """Lấy trạng thái máy in."""
        return {
            "available": self.available,
            "name": self.printer_name
        }
