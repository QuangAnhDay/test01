# ==========================================
# BACKGROUND WORKERS (QThread Classes)
# ==========================================
"""
File này chứa tất cả các class QThread để xử lý tác vụ nền.
"""

import time
import requests
import cloudinary
import cloudinary.uploader
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from configs import APP_CONFIG


# ==========================================
# CLOUDINARY UPLOAD THREAD
# ==========================================

class CloudinaryUploadThread(QThread):
    """Thread để upload ảnh lên Cloudinary mà không block UI."""
    
    # Signals
    upload_success = pyqtSignal(str)  # Emit URL khi thành công
    upload_error = pyqtSignal(str)    # Emit thông báo lỗi
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        try:
            # Upload lên Cloudinary
            result = cloudinary.uploader.upload(
                self.image_path,
                folder="photobooth",
                resource_type="image"
            )
            # Emit URL khi thành công
            self.upload_success.emit(result['secure_url'])
        except Exception as e:
            # Emit lỗi
            self.upload_error.emit(str(e))


# ==========================================
# THREAD TẢI ẢNH QR TỪ VIETQR
# ==========================================

class QRImageLoaderThread(QThread):
    """Thread tải ảnh QR từ VietQR API để không block UI."""
    image_loaded = pyqtSignal(QPixmap)
    load_error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
            img_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.image_loaded.emit(pixmap)
        except Exception as e:
            self.load_error.emit(str(e))


# ==========================================
# THREAD KIỂM TRA GIAO DỊCH CASSO
# ==========================================

class CassoCheckThread(QThread):
    """
    Thread kiểm tra giao dịch từ Casso API mỗi 3 giây.
    Khi tìm thấy giao dịch khớp số tiền và nội dung, phát signal.
    """
    payment_received = pyqtSignal()  # Signal khi nhận được tiền
    check_error = pyqtSignal(str)    # Signal khi có lỗi
    
    def __init__(self, amount, description):
        super().__init__()
        self.amount = amount
        self.description = description.upper()
        self.running = True
    
    def stop(self):
        """Dừng thread."""
        self.running = False
    
    def run(self):
        api_key = APP_CONFIG.get('casso_api_key', '')
        if not api_key:
            self.check_error.emit("Chưa cấu hình Casso API Key")
            return
        
        headers = {
            "Authorization": f"Apikey {api_key}",
            "Content-Type": "application/json"
        }
        
        while self.running:
            try:
                # Gọi API Casso lấy danh sách giao dịch
                response = requests.get(
                    "https://oauth.casso.vn/v2/transactions",
                    headers=headers,
                    params={"pageSize": 20, "sort": "DESC"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    transactions = data.get('data', {}).get('records', [])
                    
                    for trans in transactions:
                        trans_amount = trans.get('amount', 0)
                        trans_desc = trans.get('description', '').upper()
                        
                        # Kiểm tra khớp số tiền và nội dung chuyển khoản
                        if trans_amount >= self.amount and self.description in trans_desc:
                            self.payment_received.emit()
                            return
                
                # Chờ 3 giây trước khi kiểm tra lại
                for _ in range(30):  # 3 giây = 30 x 0.1s
                    if not self.running:
                        return
                    time.sleep(0.1)
                    
            except Exception as e:
                self.check_error.emit(str(e))
                time.sleep(3)
