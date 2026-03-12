# ==========================================
# PAYMENT HANDLER - Quản lý quy trình thanh toán
# ==========================================
"""
Xử lý các bước thanh toán:
- Tạo mã giao dịch (transaction code)
- Tạo URL VietQR
- Khởi chạy QR loader thread
- Khởi chạy Casso check thread
"""

from PyQt5.QtCore import QObject, pyqtSignal
from src.shared.types.models import (
    generate_unique_code, generate_vietqr_url,
    APP_CONFIG
)
from src.services.payment.payment_service import QRImageLoaderThread, CassoCheckThread


class PaymentHandler(QObject):
    """Xử lý logic thanh toán cho Photobooth."""
    payment_success = pyqtSignal()
    qr_loaded = pyqtSignal(object) # QPixmap
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.casso_thread = None
        self.qr_loader_thread = None
        self.current_transaction_code = ""
        self.current_amount = 0

    def start_payment_process(self, amount):
        """Khởi động quy trình thanh toán mới."""
        self.current_amount = amount
        self.current_transaction_code = generate_unique_code()
        
        # 1. Tạo URL VietQR
        
        qr_url = generate_vietqr_url(amount, self.current_transaction_code)
        
        # 2. Tải ảnh QR (thread phụ)
        self.qr_loader_thread = QRImageLoaderThread(qr_url)
        self.qr_loader_thread.image_loaded.connect(self.qr_loaded.emit)
        self.qr_loader_thread.load_error.connect(self.error_occurred.emit)
        self.qr_loader_thread.start()
        
        # 3. Chạy thread kiểm tra Casso
        self.stop_checks()
        self.casso_thread = CassoCheckThread(amount, self.current_transaction_code)
        self.casso_thread.payment_received.connect(self.payment_success.emit)
        self.casso_thread.check_error.connect(lambda msg: print(f"[PAYMENT ERROR] {msg}"))
        self.casso_thread.start()
        
        print(f"[PAYMENT] Started: {self.current_transaction_code} - {amount} VND")

    def stop_checks(self):
        """Dừng tất cả các thread kiểm tra thanh toán."""
        if self.casso_thread:
            self.casso_thread.stop()
            self.casso_thread.wait()
            self.casso_thread = None
        
        if self.qr_loader_thread:
            self.qr_loader_thread.terminate()
            self.qr_loader_thread.wait()
            self.qr_loader_thread = None
