# ==========================================
# SYSTEM CHECK UTILITIES
# ==========================================
"""
Kiểm tra phần cứng hệ thống (máy in, v.v.).
"""

import os
import subprocess


def check_printer_available():
    """Kiểm tra xem có máy in nào được kết nối không (Windows)."""
    if os.name != 'nt':
        return False, "Chỉ hỗ trợ Windows"

    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Printer | Select-Object -ExpandProperty Name'],
            capture_output=True, text=True, timeout=5
        )
        printers = result.stdout.strip().split('\n')
        printers = [p.strip() for p in printers if p.strip()]

        if printers:
            return True, printers[0]
        else:
            return False, "Không tìm thấy máy in"
    except Exception as e:
        return False, str(e)
