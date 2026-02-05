# ==========================================
# BACKGROUND WORKERS (QThread Classes)
# ==========================================
"""
File này chứa tất cả các class QThread để xử lý tác vụ nền.
"""

import time
import os
import requests
import cloudinary
import cloudinary.uploader
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from config.settings import APP_CONFIG


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
            # Upload lên Cloudinary - Tự động nhận diện resource_type (image/video)
            result = cloudinary.uploader.upload(
                self.image_path,
                folder="photobooth",
                resource_type="auto"
            )
            # Emit URL khi thành công
            self.upload_success.emit(result['secure_url'])
        except Exception as e:
            # Emit lỗi
            self.upload_error.emit(str(e))


class CloudinaryLandingPageThread(QThread):
    """Thread để upload ảnh, video và tạo 1 trang HTML làm landing page chứa cả 2."""
    upload_success = pyqtSignal(str) # URL của file HTML
    upload_error = pyqtSignal(str)
    
    def __init__(self, image_path, video_path):
        super().__init__()
        self.image_path = image_path
        self.video_path = video_path

    def run(self):
        try:
            # 1. Upload Photo
            p_res = cloudinary.uploader.upload(
                self.image_path, 
                folder="photobooth", 
                resource_type="image"
            )
            p_url = p_res['secure_url']
            
            # 2. Upload Video
            v_url = ""
            if self.video_path and os.path.exists(self.video_path):
                v_res = cloudinary.uploader.upload(
                    self.video_path, 
                    folder="photobooth", 
                    resource_type="video"
                )
                v_url = v_res['secure_url']
            
            # 3. Tạo HTML Landing Page
            html_content = f"""
            <!DOCTYPE html>
            <html lang="vi">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Kỷ niệm Photobooth của bạn</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        text-align: center; 
                        background-color: #f4f7f6; 
                        color: #2c3e50; 
                        margin: 0; padding: 20px;
                    }}
                    .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    h1 {{ color: #709a8a; font-size: 24px; }}
                    img, video {{ max-width: 100%; border-radius: 15px; margin-top: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
                    .btn-group {{ margin-top: 30px; display: flex; flex-direction: column; gap: 10px; }}
                    .btn {{ 
                        display: block; padding: 15px; 
                        background-color: #709a8a; color: white; 
                        text-decoration: none; border-radius: 10px; 
                        font-weight: bold; transition: 0.3s;
                    }}
                    .btn:hover {{ background-color: #5d8476; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #999; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✨ Kỷ niệm Photobooth ✨</h1>
                    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!</p>
                    
                    <div class="media">
                        <img src="{p_url}" alt="Ảnh Photobooth">
                        {f'<video src="{v_url}" controls autoplay muted playsinline></video>' if v_url else ""}
                    </div>

                    <div class="btn-group">
                        <a href="{p_url}" download="photo.jpg" class="btn">⬇️ Tải Ảnh Thành Phẩm</a>
                        {f'<a href="{v_url}" download="video.mp4" class="btn">⬇️ Tải Video Quá Trình</a>' if v_url else ""}
                    </div>

                    <div class="footer">
                        Powered by QuangAnhDay's Photobooth
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Lưu tạm file HTML
            temp_html = self.image_path + ".html"
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # 4. Upload HTML lên Cloudinary (dạng raw)
            h_res = cloudinary.uploader.upload(
                temp_html, 
                folder="photobooth/pages", 
                resource_type="raw",
                public_id=os.path.basename(temp_html)
            )
            
            # Xóa file tạm
            try: os.remove(temp_html)
            except: pass
            
            self.upload_success.emit(h_res['secure_url'])
            
        except Exception as e:
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
