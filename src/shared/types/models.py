# ==========================================
# CẤU HÌNH & MÔ HÌNH DỮ LIỆU TOÀN CỤC
# ==========================================
"""
File này chứa tất cả các biến cấu hình toàn cục,
các hàm quản lý config, và các hằng số.
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
FIRST_PHOTO_DELAY = 10   # Giây cho ảnh đầu tiên
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
    url = f"https://img.vietqr.io/image/{bank_bin}-{account}-compact2.png"
    url += f"?amount={amount}&addInfo={description}&accountName={name}"
    return url


# ==========================================
# CẤU HÌNH KÍCH THƯỚC KHUNG ẢNH
# ==========================================

# 4x1: 4 ảnh dọc (Strip)
LAYOUT_4x1 = {
    "CANVAS_W": 551,
    "CANVAS_H": 1517,
    "PAD_TOP": 48,
    "PAD_BOTTOM": 186,
    "PAD_LEFT": 53,
    "PAD_RIGHT": 53,
    "GAP": 32,
}

# ==========================================
# CUSTOM LAYOUTS (Đọc từ file JSON)
# ==========================================
CUSTOM_LAYOUTS_FILE = "custom_layouts.json"
CUSTOM_LAYOUTS = {}

def load_custom_layouts():
    """Tải các layout custom từ file json."""
    global CUSTOM_LAYOUTS
    CUSTOM_LAYOUTS.clear()  # Đảm bảo xóa trắng trước khi nạp lại
    
    if not os.path.exists(CUSTOM_LAYOUTS_FILE) or os.path.getsize(CUSTOM_LAYOUTS_FILE) == 0:
        return {}
        
    try:
        with open(CUSTOM_LAYOUTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
                
            # Chuyển list sang tuple cho SLOTS nếu cần
            for key, val in data.items():
                if "SLOTS" in val:
                    val["SLOTS"] = [tuple(s) for s in val["SLOTS"]]
            
            CUSTOM_LAYOUTS.update(data)
            print(f"[DEBUG] load_custom_layouts: Loaded {len(CUSTOM_LAYOUTS)} layouts")
            return CUSTOM_LAYOUTS
    except Exception as e:
        print(f"Lỗi đọc custom_layouts.json: {e}")
        return {}

# Load ngay khi import
load_custom_layouts()


DEFAULT_LAYOUTS = {
    "4x1": LAYOUT_4x1,
}


def get_layout_config(layout_type):
    """Lấy cấu hình cho từng layout."""
    # Kiểm tra trong các layout mặc định trước
    if layout_type in DEFAULT_LAYOUTS:
        return DEFAULT_LAYOUTS[layout_type]
    
    # Reload để đảm bảo layout mới nhất từ admin
    load_custom_layouts()
    if layout_type in CUSTOM_LAYOUTS:
        cfg = CUSTOM_LAYOUTS[layout_type]
        print(f"[DEBUG] get_layout_config(Custom): {layout_type} -> {len(cfg.get('SLOTS', []))} slots")
        return cfg
    
    print(f"[DEBUG] get_layout_config(Default): {layout_type} (falling back to 4x1)")
    return DEFAULT_LAYOUTS.get("4x1")


def get_all_layouts():
    """Trả về tất cả layouts (mặc định + custom)."""
    load_custom_layouts()
    all_layouts = DEFAULT_LAYOUTS.copy()
    all_layouts.update(CUSTOM_LAYOUTS)
    return all_layouts


def save_custom_layout(name, config, group="custom"):
    """Lưu một cấu hình layout custom mới vào file JSON kèm theo nhóm."""
    current_layouts = load_custom_layouts()
    
    # Ép kiểu SLOTS thành list để JSONify được
    slots_list = []
    if "SLOTS" in config:
        slots_list = [list(s) for s in config["SLOTS"]]
    
    current_layouts[name] = {
        "CANVAS_W": config.get("CANVAS_W", 800),
        "CANVAS_H": config.get("CANVAS_H", 1200),
        "SLOTS": slots_list,
        "group": group  # Phân loại: 'vertical' hoặc 'custom'
    }
    
    try:
        with open(CUSTOM_LAYOUTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_layouts, f, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi ghi custom_layouts.json: {e}")
        return False

def delete_custom_layout(name):
    """Xóa một layout custom khỏi file JSON."""
    current_layouts = load_custom_layouts()
    if name in current_layouts:
        del current_layouts[name]
        try:
            with open(CUSTOM_LAYOUTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_layouts, f, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi xóa layout: {e}")
            return False
    return False

