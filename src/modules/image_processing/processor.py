# ==========================================
# IMAGE PROCESSOR - Xử lý ảnh, tạo collage
# ==========================================
"""
Module xử lý ảnh: tạo collage, chèn template, 
filter, tạo khung ảnh.
"""

import os
import cv2
import numpy as np
from src.shared.types.models import (
    TEMPLATE_DIR, get_layout_config, get_all_layouts,
    LAYOUT_4x1,
    CUSTOM_LAYOUTS
)
from src.shared.utils.helpers import overlay_images


def generate_frame_templates():
    """Tạo file ảnh khung nền trong suốt/màu cho các layout nếu chưa có."""
    base_dir = TEMPLATE_DIR
    os.makedirs(base_dir, exist_ok=True)

    # 1. Xử lý các custom layouts - đặt vào đúng thư mục group
    custom_dir = os.path.join(base_dir, "custom")
    vertical_dir = os.path.join(base_dir, "vertical")
    os.makedirs(custom_dir, exist_ok=True)
    os.makedirs(vertical_dir, exist_ok=True)
    
    # Tập hợp tên layout còn tồn tại để dọn file mồ côi
    valid_custom_names = set(CUSTOM_LAYOUTS.keys())
    
    for name, cfg in CUSTOM_LAYOUTS.items():
        # Xác định thư mục dựa trên group
        group = cfg.get("group", "custom")
        if group == "vertical":
            target_dir = vertical_dir
        else:
            target_dir = custom_dir
        
        filename = os.path.join(target_dir, f"frame_{name}.png")
        if not os.path.exists(filename):
            print(f"Creating custom frame: {filename}")
            w, h = cfg["CANVAS_W"], cfg["CANVAS_H"]
            # Tạo nền trắng đục (alpha=255)
            frame = np.ones((h, w, 4), dtype=np.uint8) * 255
            cv2.putText(frame, f"CUSTOM: {name}", (50, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100, 255), 2)
            # Khoét vùng slot trong suốt (alpha=0) để ảnh hiện ra
            for slot in cfg.get("SLOTS", []):
                sx, sy, sw, sh = slot
                y1, y2 = max(0, sy), min(h, sy + sh)
                x1, x2 = max(0, sx), min(w, sx + sw)
                frame[y1:y2, x1:x2] = [0, 0, 0, 0]
            cv2.imwrite(filename, frame)
        
        # Xóa file ở thư mục SAI (nếu trước đó bị đặt nhầm)
        wrong_dir = vertical_dir if group != "vertical" else custom_dir
        wrong_path = os.path.join(wrong_dir, f"frame_{name}.png")
        if os.path.exists(wrong_path):
            print(f"[CLEANUP] Removing misplaced template: {wrong_path}")
            os.remove(wrong_path)

    # Dọn các file template mồ côi trong thư mục custom
    # (template có tên frame_Custom_X.png nhưng layout Custom_X đã bị xóa)
    import re
    for f in os.listdir(custom_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and f.startswith('frame_'):
            fname_no_ext = os.path.splitext(f)[0]
            # Trích tên layout từ tên file (frame_{layout_name}.png hoặc frame_{layout_name}_suffix.png)
            rest = fname_no_ext[len('frame_'):]
            m = re.match(r'^(Custom_\d+)', rest)
            if m:
                layout_name = m.group(1)
                if layout_name not in valid_custom_names:
                    orphan_path = os.path.join(custom_dir, f)
                    print(f"[CLEANUP] Removing orphaned template: {orphan_path} (layout '{layout_name}' no longer exists)")
                    os.remove(orphan_path)



def crop_to_aspect_wh(img, target_w, target_h):
    """Crop ảnh về đúng tỷ lệ trước khi resize để tránh méo."""
    if img is None:
        return np.zeros((target_h, target_w, 3), np.uint8)

    h, w = img.shape[:2]
    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        return img[:, start_x:start_x + new_w]
    else:
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        return img[start_y:start_y + new_h, :]


def create_collage(images, layout_type):
    """Tạo collage từ các ảnh đã chọn dựa trên kiểu bố cục với padding."""
    count = len(images)

    try:
        import importlib
        from src.shared.types import models as frame_config_module
        importlib.reload(frame_config_module)
        config = frame_config_module.get_layout_config(layout_type)

        PAD_TOP = config.get("PAD_TOP", 20)
        PAD_BOTTOM = config.get("PAD_BOTTOM", 100)
        PAD_LEFT = config.get("PAD_LEFT", 20)
        PAD_RIGHT = config.get("PAD_RIGHT", 20)
        GAP = config.get("GAP", 15)
        CANVAS_W = config.get("CANVAS_W", 1280)
        CANVAS_H = config.get("CANVAS_H", 720)

        print(f"DEBUG: Loaded config for {layout_type}: {CANVAS_W}x{CANVAS_H}")
    except Exception as e:
        print(f"WARNING: Cannot load config ({e}). Using defaults.")
        config = {}
        PAD_TOP, PAD_BOTTOM, PAD_LEFT, PAD_RIGHT, GAP = 20, 100, 20, 20, 15
        if layout_type == "2x1":
            CANVAS_W, CANVAS_H = 640, 900
        elif layout_type == "4x1":
            CANVAS_W, CANVAS_H = 640, 1600
        else:
            CANVAS_W, CANVAS_H = 1210, 1810

    if count == 0:
        return np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)

    # HỖ TRỢ LAYOUT CUSTOM (SLOTS)
    if "SLOTS" in config:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        slots = config["SLOTS"]
        for i, img in enumerate(images):
            if i >= len(slots):
                break
            sx, sy, sw, sh = slots[i]
            cropped = crop_to_aspect_wh(img, sw, sh)
            resized = cv2.resize(cropped, (sw, sh))
            canvas[sy:sy + sh, sx:sx + sw] = resized
        return canvas

    if count == 2:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        if layout_type == "1x2":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM
            img_w = available_w // 2
            img_h = available_h
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT + i * (img_w + GAP)
                y = PAD_TOP
                canvas[y:y + img_h, x:x + img_w] = resized
        elif layout_type == "2x1":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT
                y = PAD_TOP + i * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        else:
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM
            img_w = available_w // 2
            img_h = available_h
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT + i * (img_w + GAP)
                y = PAD_TOP
                canvas[y:y + img_h, x:x + img_w] = resized

    elif count == 4:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        if layout_type == "2x2":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w // 2
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                row = i // 2
                col = i % 2
                x = PAD_LEFT + col * (img_w + GAP)
                y = PAD_TOP + row * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        elif layout_type == "4x1":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - 3 * GAP
            img_w = available_w
            img_h = available_h // 4
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT
                y = PAD_TOP + i * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        else:
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w // 2
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                row = i // 2
                col = i % 2
                x = PAD_LEFT + col * (img_w + GAP)
                y = PAD_TOP + row * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
    else:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)

    return canvas


def load_templates_for_layout(layout_type, selected_frame_count):
    """Load danh sách templates cho một nhóm layout (vertical hoặc custom)."""
    templates = []
    
    # Xác định nhóm (group) của layout để tìm đúng thư mục template
    from src.shared.types.models import get_layout_config
    cfg = get_layout_config(layout_type)
    layout_group = cfg.get("group", "vertical" if layout_type == "4x1" else "custom")
    
    # Danh sách các thư mục cần quét ảnh
    search_dirs = []
    
    if layout_group == "vertical" or layout_type == "4x1":
        search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
    else:
        search_dirs.append(os.path.join(TEMPLATE_DIR, "custom"))

    # Tiến hành quét các thư mục đã xác định
    for directory in search_dirs:
        if os.path.exists(directory):
            for f in os.listdir(directory):
                fpath = os.path.join(directory, f)
                if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.abspath(fpath)
                    
                    # Quy tắc: frame_{layout_type}.png HOẶC frame_{layout_type}_suffix.png
                    fname_no_ext = os.path.splitext(f)[0]
                    exact_match = f"frame_{layout_type}"
                    variant_prefix = f"frame_{layout_type}_"
                    
                    if fname_no_ext == exact_match or fname_no_ext.startswith(variant_prefix):
                        if full_path not in templates:
                            templates.append(full_path)
                    else:
                        continue # Bỏ qua template của layout khác

    print(f"[DEBUG] Templates for {layout_type}: {templates}")
    return templates


def load_all_templates_for_group(group_name):
    """Load TẤT CẢ templates trong một nhóm (vertical hoặc custom), không phân biệt layout."""
    templates = []
    
    # Danh sách các thư mục cần quét
    search_dirs = []
    
    if group_name == "vertical":
        search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
    else:
        search_dirs.append(os.path.join(TEMPLATE_DIR, "custom"))

    # Lấy danh sách layout hợp lệ cho nhóm custom để lọc template mồ côi
    valid_layout_names = None
    if group_name == "custom":
        all_layouts = get_all_layouts()
        valid_layout_names = set()
        for lname, lcfg in all_layouts.items():
            lgroup = lcfg.get("group", "vertical" if lname == "4x1" else "custom")
            if lgroup == "custom":
                valid_layout_names.add(lname)

    # Quét tất cả file ảnh trong các thư mục
    for directory in search_dirs:
        if os.path.exists(directory):
            for f in sorted(os.listdir(directory)):
                fpath = os.path.join(directory, f)
                if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # Với nhóm custom: chỉ load template có layout config tồn tại
                    if valid_layout_names is not None:
                        detected = detect_layout_from_template(fpath)
                        if detected and detected not in valid_layout_names:
                            continue  # Bỏ qua template mồ côi
                    
                    full_path = os.path.abspath(fpath)
                    if full_path not in templates:
                        templates.append(full_path)

    print(f"[DEBUG] All templates for group '{group_name}': {templates}")
    return templates


def detect_layout_from_template(template_path):
    """Phát hiện layout_type từ tên file template.
    
    Quy tắc: frame_{layout_type}.png hoặc frame_{layout_type}_suffix.png
    Ví dụ: frame_4x1.png -> '4x1', frame_Custom_3_tet.png -> 'Custom_3'
    """
    import re
    fname = os.path.splitext(os.path.basename(template_path))[0]
    
    # Bỏ prefix "frame_"
    if fname.startswith("frame_"):
        rest = fname[len("frame_"):]
    else:
        return None
    
    # Thử khớp với pattern Custom_N trước
    m = re.match(r'^(Custom_\d+)', rest)
    if m:
        return m.group(1)
    
    # Thử khớp layout đơn giản như 4x1, 2x2, ...
    m = re.match(r'^(\d+x\d+)', rest)
    if m:
        return m.group(1)
    
    # Thử khớp tên layout đơn (ví dụ: "5", "6")
    m = re.match(r'^(\d+)', rest)
    if m:
        return m.group(1)
    
    return rest.split("_")[0] if "_" in rest else rest



def apply_template_overlay(collage_image, template_path):
    """Áp dụng template lên collage."""
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is not None and collage_image is not None:
        return overlay_images(collage_image.copy(), template)
    return collage_image
