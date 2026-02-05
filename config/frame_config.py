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
    },
    "Custom_Custom1": {
        "CANVAS_W": 1286,
        "CANVAS_H": 652,
        "SLOTS": [
            (36, 36, 586, 397),
            (664, 36, 586, 397)
        ]
    },
    "Custom_Custom2": {
        "CANVAS_W": 987,
        "CANVAS_H": 775,
        "SLOTS": [
            (58, 46, 401, 305),
            (519, 45, 400, 300),
            (56, 391, 400, 300),
            (507, 395, 400, 300)
        ]
    },
}

def save_custom_layout(name, config):
    """Lưu một cấu hình layout custom mới vào file frame_config.py."""
    import inspect
    import os

    # Đọc nội dung file hiện tại
    file_path = __file__
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Tìm vị trí biến CUSTOM_LAYOUTS
    start_line = -1
    end_line = -1
    bracket_count = 0
    in_custom = False

    for i, line in enumerate(lines):
        if "CUSTOM_LAYOUTS = {" in line:
            start_line = i
            in_custom = True
            bracket_count = 1
            continue
        
        if in_custom:
            bracket_count += line.count('{') - line.count('}')
            if bracket_count == 0:
                end_line = i
                break

    if start_line != -1 and end_line != -1:
        # Tạo chuỗi config mới
        new_entry = f"    \"{name}\": {{\n"
        new_entry += f"        \"CANVAS_W\": {config['CANVAS_W']},\n"
        new_entry += f"        \"CANVAS_H\": {config['CANVAS_H']},\n"
        new_entry += "        \"SLOTS\": [\n"
        for j, (x, y, w, h) in enumerate(config.get('SLOTS', [])):
            comma = "," if j < len(config['SLOTS']) - 1 else ""
            new_entry += f"            ({x}, {y}, {w}, {h}){comma}\n"
        new_entry += "        ]\n"
        new_entry += "    },\n"

        # Chèn vào trước dấu đóng ngoặc cuối cùng của CUSTOM_LAYOUTS
        lines.insert(end_line, new_entry)

        # Ghi lại file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False



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
    base_dir = "templates"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Xử lý các custom layouts (Lưu vào thư mục templates/custom/)
    custom_dir = os.path.join(base_dir, "custom")
    os.makedirs(custom_dir, exist_ok=True)
    for name, cfg in CUSTOM_LAYOUTS.items():
        filename = os.path.join(custom_dir, f"frame_{name}.png")
        if not os.path.exists(filename):
            print(f"Creating custom frame: {filename}")
            w, h = cfg["CANVAS_W"], cfg["CANVAS_H"]
            frame = np.zeros((h, w, 4), dtype=np.uint8)
            frame[:] = [138, 154, 112, 255] # Sage Green
            cv2.putText(frame, f"CUSTOM: {name}", (50, h - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 2)
            cv2.imwrite(filename, frame)
    
    # 2. Xử lý các mặc định (Lưu vào thư mục con theo tên layout, ví dụ: templates/1x2/)
    layouts = {
        "1x2": LAYOUT_1x2,
        "2x1": LAYOUT_2x1,
        "2x2": LAYOUT_2x2,
        "4x1": LAYOUT_4x1,
    }
    for name, cfg in layouts.items():
        layout_dir = os.path.join(base_dir, name)
        os.makedirs(layout_dir, exist_ok=True)
        filename = os.path.join(layout_dir, f"frame_{name}.png")
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
    print("[OK] Cac file khung da duoc cap nhat tai thu muc /templates")
