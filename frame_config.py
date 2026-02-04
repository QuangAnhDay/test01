import os
import cv2
import numpy as np

# ==========================================
# CẤU HÌNH KÍCH THƯỚC KHUNG ẢNH
# ==========================================

# 1x2: 2 ảnh ngang
LAYOUT_1x2 = {
    "CANVAS_W": 943,
    "CANVAS_H": 974,
    "PAD_TOP": 50,
    "PAD_BOTTOM": 50,
    "PAD_LEFT": 63,
    "PAD_RIGHT": 249,
    "GAP": 37,
}

# 2x1: 2 ảnh dọc
LAYOUT_2x1 = {
    "CANVAS_W": 1286,
    "CANVAS_H": 652,
    "PAD_TOP": 53,
    "PAD_BOTTOM": 219,
    "PAD_LEFT": 48,
    "PAD_RIGHT": 48,
    "GAP": 42,
}

# 2x2: 4 ảnh ô vuông
LAYOUT_2x2 = {
    "CANVAS_W": 933,
    "CANVAS_H": 782,
    "PAD_TOP": 30,
    "PAD_BOTTOM": 156,
    "PAD_LEFT": 30,
    "PAD_RIGHT": 30,
    "GAP": 35,
}

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
# CUSTOM LAYOUTS (Dành cho kéo thả/tùy chỉnh vị trí tự do)
# ==========================================
# Nếu muốn tự định nghĩa vị trí từng ảnh, dùng mảng "SLOTS"
# Định dạng: (x, y, width, height)
CUSTOM_LAYOUTS = {
    "Custom_Layout": {
        "CANVAS_W": 1209,
        "CANVAS_H": 1517,
        "SLOTS": [
            (82, 56, 400, 300),
            (64, 512, 400, 300),
            (673, 118, 400, 300),
            (599, 566, 400, 300)
        ]
    }
}

DEFAULT_LAYOUTS = {
    "1x2": LAYOUT_1x2,
    "2x1": LAYOUT_2x1,
    "2x2": LAYOUT_2x2,
    "4x1": LAYOUT_4x1,
}

def get_layout_config(layout_type):
    """Lấy cấu hình cho từng layout."""
    # Ưu tiên tìm trong CUSTOM_LAYOUTS
    if layout_type in CUSTOM_LAYOUTS:
        return CUSTOM_LAYOUTS[layout_type]
    return DEFAULT_LAYOUTS.get(layout_type, LAYOUT_1x2)

def get_all_layouts():
    """Trả về tất cả layouts (mặc định + custom)."""
    all_layouts = DEFAULT_LAYOUTS.copy()
    all_layouts.update(CUSTOM_LAYOUTS)
    return all_layouts

def generate_frame_templates():
    """Tạo file ảnh khung nền trong suốt/màu cho các layout nếu chưa có."""
    os.makedirs("templates", exist_ok=True)
    os.makedirs("templates/custom", exist_ok=True)
    
    layouts = {
        "1x2": LAYOUT_1x2,
        "2x1": LAYOUT_2x1,
        "2x2": LAYOUT_2x2,
        "4x1": LAYOUT_4x1,
    }
    # Xử lý các custom layouts (Lưu vào thư mục riêng)
    for name, cfg in CUSTOM_LAYOUTS.items():
        filename = f"templates/custom/frame_{name}.png"
        if not os.path.exists(filename):
            print(f"Creating custom frame: {filename}")
            w, h = cfg["CANVAS_W"], cfg["CANVAS_H"]
            frame = np.zeros((h, w, 4), dtype=np.uint8)
            frame[:] = [138, 154, 112, 255] # Sage Green
            cv2.putText(frame, f"CUSTOM: {name}", (50, h - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 2)
            cv2.imwrite(filename, frame)
    
    # Xử lý các mặc định
    for name, cfg in layouts.items():
        filename = f"templates/frame_{name}.png"
        if not os.path.exists(filename):
            print(f"Creating default frame: {filename}")
            w, h = cfg["CANVAS_W"], cfg["CANVAS_H"]
            frame = np.zeros((h, w, 4), dtype=np.uint8)
            frame[:] = [138, 154, 112, 255] # Sage Green
            cv2.putText(frame, f"DEFAULT: {name}", (50, h - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 2)
            cv2.imwrite(filename, frame)

if __name__ == "__main__":
    generate_frame_templates()
    print("Xong! Các file khung đã được cập nhật tại thư mục /templates")
