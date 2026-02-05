# ==========================================
# CẤU HÌNH TOÀN CỤC (GLOBAL CONFIGURATION)
# ==========================================
"""
File này chứa tất cả các biến cấu hình toàn cục và các hàm liên quan đến config.
"""

import os
import json
import random
import string

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
CONFIG_FILE = "config.json"
WINDOW_TITLE = "Photobooth Cảm Ứng"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CAMERA_INDEX = 0
FIRST_PHOTO_DELAY = 10  # Giây cho ảnh đầu tiên
BETWEEN_PHOTO_DELAY = 1  # Giây giữa các ảnh
PHOTOS_TO_TAKE = 10
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "output"
SAMPLE_PHOTOS_DIR = "sample_photos"

# ==========================================
# BIẾN TOÀN CỤC CHO CẤU HÌNH
# ==========================================
APP_CONFIG = {}


# ==========================================
# HÀM QUẢN LÝ CẤU HÌNH
# ==========================================

def load_config():
    """Tải cấu hình từ file config.json."""
    global APP_CONFIG
    if not os.path.exists(CONFIG_FILE):
        return False
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            new_config = json.load(f)
            # Cập nhật vào dictionary toàn cục (update in-place)
            APP_CONFIG.clear()
            APP_CONFIG.update(new_config)
        
        # Cấu hình Cloudinary từ config
        cloud_config = APP_CONFIG.get('cloudinary', {})
        if all([cloud_config.get('cloud_name'), cloud_config.get('api_key'), cloud_config.get('api_secret')]):
            import cloudinary
            cloudinary.config(
                cloud_name=cloud_config.get('cloud_name'),
                api_key=cloud_config.get('api_key'),
                api_secret=cloud_config.get('api_secret'),
                secure=True
            )
        return True
    except Exception as e:
        print(f"Lỗi đọc config: {e}")
        return False


def get_price_2():
    """Lấy giá gói 2 ảnh từ config."""
    return APP_CONFIG.get('price_2_photos', 20000)


def get_price_4():
    """Lấy giá gói 4 ảnh từ config."""
    return APP_CONFIG.get('price_4_photos', 35000)


def get_price_by_layout(layout_name):
    """Lấy giá cho một layout cụ thể từ config hoặc dùng giá mặc định."""
    prices = APP_CONFIG.get('layout_prices', {})
    if layout_name in prices:
        return prices[layout_name]
    
    # Fallback to default group prices
    # Determine photo count for default layouts
    if layout_name in ["1x2", "2x1"]:
        return get_price_2()
    return get_price_4()


def get_all_prices():
    """Lấy dictionary giá của tất cả layout."""
    return APP_CONFIG.get('layout_prices', {})


def format_price(amount):
    """Format số tiền thành chuỗi VNĐ."""
    return f"{amount:,}".replace(",", ".") + " VNĐ"


def generate_unique_code():
    """Tạo mã giao dịch duy nhất: PB + 4 ký tự ngẫu nhiên."""
    chars = string.ascii_uppercase + string.digits
    return "PB" + ''.join(random.choices(chars, k=4))


def generate_vietqr_url(amount, description):
    """Tạo URL VietQR động từ config."""
    bank_bin = APP_CONFIG.get('bank_bin', '')
    account = APP_CONFIG.get('bank_account', '')
    name = APP_CONFIG.get('account_name', '')
    
    # Format: https://img.vietqr.io/image/{bank_bin}-{account}-compact2.png?amount={amount}&addInfo={description}&accountName={name}
    url = f"https://img.vietqr.io/image/{bank_bin}-{account}-compact2.png"
    url += f"?amount={amount}&addInfo={description}&accountName={name}"
    return url
