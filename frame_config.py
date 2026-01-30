# ==========================================
# CẤU HÌNH KÍCH THƯỚC KHUNG ẢNH
# ==========================================
# File này chứa tất cả thông số padding và gap cho từng layout
# Sửa các giá trị dưới đây để tinh chỉnh kích thước khung

# ==========================================
# LAYOUT 1x2
# ==========================================
LAYOUT_1x2 = {
    "CANVAS_W": 943,
    "CANVAS_H": 974,
    "PAD_TOP": 50,
    "PAD_BOTTOM": 50,
    "PAD_LEFT": 63,
    "PAD_RIGHT": 249,
    "GAP": 37,
}

# ==========================================
# LAYOUT 2x1
# ==========================================
LAYOUT_2x1 = {
    "CANVAS_W": 1286,
    "CANVAS_H": 652,
    "PAD_TOP": 53,
    "PAD_BOTTOM": 219,
    "PAD_LEFT": 48,
    "PAD_RIGHT": 48,
    "GAP": 42,
}

# ==========================================
# LAYOUT 2x2
# ==========================================
LAYOUT_2x2 = {
    "CANVAS_W": 933,
    "CANVAS_H": 782,
    "PAD_TOP": 30,
    "PAD_BOTTOM": 156,
    "PAD_LEFT": 30,
    "PAD_RIGHT": 30,
    "GAP": 35,
}

# ==========================================
# LAYOUT 4x1
# ==========================================

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
# HÀM HỖ TRỢ
# ==========================================
def get_layout_config(layout_type):
    """Lấy cấu hình padding cho từng layout."""
    configs = {
        "1x2": LAYOUT_1x2,
        "2x1": LAYOUT_2x1,
        "2x2": LAYOUT_2x2,
        "4x1": LAYOUT_4x1,
    }
    return configs.get(layout_type, LAYOUT_1x2)  # Default là 1x2

# ==========================================
# GHI CHÚ
# ==========================================
# PAD_TOP: Bì phía trên - thường để nhỏ hoặc vừa phải
# PAD_BOTTOM: Bì phía dưới - thường để rộng hơn cho logo/watermark
# PAD_LEFT: Bì bên trái
# PAD_RIGHT: Bì bên phải
# GAP: Khoảng cách giữa các ảnh - có thể thêm họa tiết trang trí

# VÍ DỤ TINH CHỈNH:
# - Muốn bì dưới rộng hơn để đặt logo: PAD_BOTTOM = 150
# - Muốn bì trái/phải rộng hơn: PAD_LEFT = 50, PAD_RIGHT = 50
# - Muốn ảnh gần nhau hơn: GAP = 10
# - Muốn ảnh xa nhau hơn: GAP = 30
