# ==========================================
# CLOUD UPLOAD - Upload ảnh lên Cloud (MEMORY VERSION)
# ==========================================
"""
Module upload ảnh trực tiếp từ bộ nhớ (numpy array) lên Cloudinary,
giúp tối ưu hiệu năng và không cần ghi file tạm ra đĩa.
"""

import os
import io
import cv2
import time
import cloudinary
import cloudinary.uploader
from PyQt5.QtCore import QThread, pyqtSignal
from src.shared.types.models import APP_CONFIG


class CloudinaryUploadThread(QThread):
    """Thread để upload ảnh lên Cloudinary từ bộ nhớ (numpy array)."""
    upload_success = pyqtSignal(str)
    upload_error = pyqtSignal(str)

    def __init__(self, image_data):
        super().__init__()
        self.image_data = image_data

    def run(self):
        try:
            if self.image_data is None:
                raise ValueError("Dữ liệu ảnh trống (None)")

            # Encode ảnh sang buffer JPG
            _, buffer = cv2.imencode('.jpg', self.image_data)
            io_buf = io.BytesIO(buffer)
            
            result = cloudinary.uploader.upload(
                io_buf,
                folder="photobooth",
                resource_type="image"
            )
            self.upload_success.emit(result['secure_url'])
        except Exception as e:
            print(f"[CLOUD ERROR] Upload error: {e}")
            self.upload_error.emit(str(e))


class CloudinaryLandingPageThread(QThread):
    """Thread upload ảnh từ bộ nhớ và tạo Landing Page Cloudinary."""
    upload_success = pyqtSignal(str)
    upload_error = pyqtSignal(str)

    def __init__(self, image_data, video_path=None):
        super().__init__()
        self.image_data = image_data
        self.video_path = video_path

    def run(self):
        try:
            if self.image_data is None:
                raise ValueError("Dữ liệu ảnh trống (None)")

            # 1. Upload Photo từ Memory
            _, buffer = cv2.imencode('.jpg', self.image_data)
            io_buf = io.BytesIO(buffer)
            
            p_res = cloudinary.uploader.upload(
                io_buf,
                folder="photobooth",
                resource_type="image"
            )
            p_url = p_res['secure_url']

            # 2. Upload Video (Nếu có)
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
                        <a href="{p_url}" download="photo.jpg" class="btn">⬇️ Tải Ảnh Của Bạn</a>
                        {f'<a href="{v_url}" download="video.mp4" class="btn">⬇️ Tải Video Của Bạn</a>' if v_url else ""}
                    </div>

                    <div class="footer">
                        Powered by QuangAnhDay's Photobooth
                    </div>
                </div>
            </body>
            </html>
            """

            # 4. Upload HTML trực tiếp từ stream
            html_buf = io.BytesIO(html_content.encode('utf-8'))
            h_res = cloudinary.uploader.upload(
                html_buf,
                folder="photobooth/pages",
                resource_type="raw",
                public_id=f"page_{int(time.time())}.html"
            )

            self.upload_success.emit(h_res['secure_url'])
            
            # Tự động xóa file video nếu có (vì video vẫn đang dùng file cục bộ)
            if self.video_path and os.path.exists(self.video_path):
                try:
                    os.remove(self.video_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"[CLOUD ERROR] Landing Page error: {e}")
            self.upload_error.emit(str(e))
